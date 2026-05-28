<script setup>
import mermaid from 'mermaid'
import { computed, nextTick, onMounted, onUnmounted, shallowRef, useTemplateRef, watch } from 'vue'

import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import ToolVersionMenu from 'src/components/tools/ToolVersionMenu.vue'
import ToolWorkbench from 'src/components/tools/ToolWorkbench.vue'
import { useToolVersions } from 'src/composables/useToolVersions'

const defaultSource = `flowchart LR
  idea["写下想法"] --> shape{"选择图表"}
  shape --> flow["流程图"]
  shape --> seq["时序图"]
  shape --> gantt["计划图"]
  flow --> preview["实时预览"]
  seq --> preview
  gantt --> preview
  preview --> export["复制源码 / 下载 SVG"]`

const examples = [
  {
    name: '流程图',
    source: defaultSource
  },
  {
    name: '时序图',
    source: `sequenceDiagram
  participant U as 用户
  participant F as 前端
  participant A as API
  U->>F: 输入 Mermaid 源码
  F->>F: 防抖渲染
  F->>A: 可选保存
  A-->>F: 返回云端存档
  F-->>U: 展示预览`
  },
  {
    name: '甘特图',
    source: `gantt
  title Mermaid 预览功能
  dateFormat  YYYY-MM-DD
  section Build
  编辑器界面      :done,    editor, 2026-05-25, 1d
  实时预览        :active,  preview, 2026-05-25, 1d
  导出动作        :         export, 2026-05-26, 1d`
  }
]

const source = shallowRef(defaultSource)
const renderedSvg = shallowRef('')
const renderError = shallowRef('')
const actionError = shallowRef('')
const copied = shallowRef(false)
const rendering = shallowRef(false)
const previewRef = useTemplateRef('preview')

let renderTimer = 0
let renderSequence = 0
let themeRenderTimer = 0
let themeObserver = null

const sourceLines = computed(() => source.value.split('\n').length)
const sourceCharacters = computed(() => source.value.length)
const trimmedSource = computed(() => source.value.trim())
const canDownload = computed(() => Boolean(renderedSvg.value) && !renderError.value)
const renderStatusText = computed(() => {
  if (rendering.value) return '渲染中'
  if (renderError.value) return '语法异常'
  if (!trimmedSource.value) return '等待输入'
  return renderedSvg.value ? '预览就绪' : '待渲染'
})
const activeExampleName = computed(() => {
  const activeExample = examples.find(example => example.source === source.value)
  return activeExample?.name || '自定义'
})
const sourceMetaText = computed(() => [
  `${sourceLines.value} 行`,
  `${sourceCharacters.value} 字符`
].join(' · '))

const versions = useToolVersions('mermaid', {
  defaultTitlePrefix: 'Mermaid 图表',
  updatedFrom: 'mermaid-editor',
  buildPayload: ({ archiveKey, remark, updatedFrom }) => ({
    source: source.value,
    line_count: sourceLines.value,
    character_count: sourceCharacters.value,
    archive_key: archiveKey,
    updated_from: updatedFrom,
    remark
  }),
  applyPayload: payload => {
    if (typeof payload?.source !== 'string' || !payload.source.trim()) {
      versions.errorMessage.value = '存档源码为空'
      return false
    }
    source.value = payload.source
    actionError.value = ''
    return true
  }
})

function readThemeToken(name, fallback) {
  if (typeof window === 'undefined') return fallback
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

function isDarkTheme() {
  const theme = document.documentElement.dataset.brandTheme
  return document.documentElement.classList.contains('dark') || theme === 'terminal' || theme === 'spotify'
}

function configureMermaid() {
  const accent = readThemeToken('--brand-color-accent', '#102542')
  const border = readThemeToken('--brand-color-border', 'rgba(16, 37, 66, 0.12)')
  const muted = readThemeToken('--brand-color-muted', '#5f6b7a')
  const surface = readThemeToken('--brand-color-surface', '#ffffff')
  const surface2 = readThemeToken('--brand-color-surface-2', '#eef3f8')
  const text = readThemeToken('--brand-color-text', '#0f1723')

  mermaid.initialize({
    darkMode: isDarkTheme(),
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'base',
    themeVariables: {
      background: surface,
      clusterBkg: surface,
      clusterBorder: border,
      darkMode: isDarkTheme(),
      edgeLabelBackground: surface,
      fontFamily: readThemeToken('--brand-font-family', 'Avenir Next, Segoe UI, sans-serif'),
      lineColor: muted,
      mainBkg: surface,
      noteBkgColor: surface2,
      noteBorderColor: border,
      noteTextColor: text,
      primaryBorderColor: accent,
      primaryColor: surface2,
      primaryTextColor: text,
      secondaryBorderColor: border,
      secondaryColor: surface,
      secondaryTextColor: text,
      tertiaryBorderColor: border,
      tertiaryColor: surface2,
      tertiaryTextColor: text,
      textColor: text
    }
  })
}

function watchThemeChanges() {
  themeObserver = new MutationObserver(() => {
    window.clearTimeout(themeRenderTimer)
    themeRenderTimer = window.setTimeout(() => {
      configureMermaid()
      renderDiagram()
    }, 80)
  })
  themeObserver.observe(document.documentElement, {
    attributeFilter: ['class', 'data-brand-theme'],
    attributes: true
  })
}

function bindRenderedDiagram(result, sequence) {
  if (sequence !== renderSequence || typeof result.bindFunctions !== 'function') return

  const previewElement = previewRef.value
  if (!previewElement) return

  try {
    result.bindFunctions(previewElement)
  } catch (error) {
    void error
  }
}

function cleanupMermaidArtifacts() {
  document.querySelectorAll('[id^="dmermaid"], [id^="mermaid-preview-"]').forEach((node) => {
    if (!previewRef.value?.contains(node)) {
      node.remove()
    }
  })
}

function formatMermaidError(error) {
  const rawMessage = error?.str || error?.message || String(error || '')
  return rawMessage
    .replace(/^Error:\s*/i, '')
    .trim() || 'Mermaid 渲染失败，请检查语法。'
}

async function renderDiagram() {
  const currentSequence = ++renderSequence
  rendering.value = true
  renderError.value = ''
  cleanupMermaidArtifacts()

  try {
    if (!trimmedSource.value) {
      renderedSvg.value = ''
      return
    }

    const id = `mermaid-preview-${Date.now()}-${currentSequence}`
    const result = await mermaid.render(id, trimmedSource.value)
    if (currentSequence !== renderSequence) return

    renderedSvg.value = result.svg
    await nextTick()
    bindRenderedDiagram(result, currentSequence)
  } catch (error) {
    if (currentSequence !== renderSequence) return
    renderedSvg.value = ''
    renderError.value = formatMermaidError(error)
  } finally {
    cleanupMermaidArtifacts()
    if (currentSequence === renderSequence) {
      rendering.value = false
    }
  }
}

function scheduleRender() {
  window.clearTimeout(renderTimer)
  renderTimer = window.setTimeout(() => {
    renderDiagram()
  }, 260)
}

function useExample(example) {
  source.value = example.source
  actionError.value = ''
}

function resetSource() {
  source.value = defaultSource
  actionError.value = ''
}

async function copySource() {
  try {
    await navigator.clipboard.writeText(source.value)
    copied.value = true
    actionError.value = ''
    window.setTimeout(() => {
      copied.value = false
    }, 1400)
  } catch (error) {
    actionError.value = formatMermaidError(error) || '复制失败'
  }
}

function downloadSvg() {
  if (!canDownload.value) return

  try {
    const blob = new Blob([renderedSvg.value], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'mermaid-preview.svg'
    link.click()
    URL.revokeObjectURL(url)
    actionError.value = ''
  } catch (error) {
    actionError.value = formatMermaidError(error) || '下载失败'
  }
}

watch(source, scheduleRender)

onMounted(async () => {
  configureMermaid()
  watchThemeChanges()
  await versions.loadInitial()
  await renderDiagram()
})

onUnmounted(() => {
  window.clearTimeout(renderTimer)
  window.clearTimeout(themeRenderTimer)
  themeObserver?.disconnect()
})
</script>

<template>
  <div class="tool-detail-page mermaid-page">
    <ToolPageHeader
      title="Mermaid"
      kicker="Mermaid · 实时预览"
    />

    <section class="tool-detail-shell mermaid-shell">
      <ToolWorkbench>
        <template #toolbar>
          <section class="mermaid-toolbar-block mermaid-toolbar-save">
            <div class="mermaid-toolbar-head">
              <div class="section-kicker">保存</div>
              <span
                v-if="versions.syncStatusText.value"
                class="mermaid-table-status"
              >{{ versions.syncStatusText.value }}</span>
            </div>

            <p class="mermaid-source-meta">{{ sourceMetaText }}</p>

            <div class="mermaid-toolbar-actions">
              <ToolVersionMenu
                :versions="versions"
                save-dialog-title="保存到云端存档"
                save-as-dialog-title="另存为新存档"
              />

              <UButton
                class="mermaid-ghost-action"
                color="neutral"
                label="重置示例"
                type="button"
                variant="subtle"
                @click="resetSource"
              />

              <UButton
                class="mermaid-ghost-action"
                color="neutral"
                :label="copied ? '已复制' : '复制源码'"
                type="button"
                variant="subtle"
                @click="copySource"
              />
              <UButton
                class="mermaid-ghost-action"
                color="neutral"
                label="下载 SVG"
                type="button"
                variant="subtle"
                :disabled="!canDownload"
                @click="downloadSvg"
              />
            </div>

            <div class="mermaid-example-strip">
              <UButton
                v-for="example in examples"
                :key="example.name"
                class="mermaid-example-item"
                color="neutral"
                :label="example.name"
                :active="activeExampleName === example.name"
                active-color="primary"
                active-variant="solid"
                :class="{ 'mermaid-example-item-active': activeExampleName === example.name }"
                type="button"
                variant="subtle"
                @click="useExample(example)"
              />
            </div>
          </section>
        </template>

        <template #source>
          <div
            v-if="versions.errorMessage.value"
            class="csv-notice csv-notice-error"
          >
            {{ versions.errorMessage.value }}
          </div>
          <div
            v-if="actionError"
            class="csv-notice csv-notice-error"
          >
            {{ actionError }}
          </div>

          <article class="mermaid-panel mermaid-editor-panel">
            <UTextarea
              v-model="source"
              class="mermaid-editor"
              placeholder="粘贴 Mermaid 源码"
              spellcheck="false"
              aria-label="Mermaid source"
              :rows="18"
              :ui="{ base: 'mermaid-editor-base' }"
            />
          </article>
        </template>

        <template #preview>
          <article
            class="mermaid-panel mermaid-preview-panel"
          >
            <div class="mermaid-preview-header">
              <span class="mermaid-table-status">{{ renderStatusText }}</span>
            </div>

            <div
              v-if="renderError"
              class="csv-notice csv-notice-error mermaid-render-error"
            >
              {{ renderError }}
            </div>

            <div
              v-if="!trimmedSource"
              class="mermaid-preview-empty"
            >
              <p class="mermaid-empty-hint">粘贴 Mermaid 源码以预览</p>
            </div>

            <div
              v-else-if="renderedSvg"
              ref="preview"
              class="mermaid-preview-canvas"
              v-html="renderedSvg"
            />

            <div
              v-else
              class="mermaid-preview-empty"
            >
              <p class="mermaid-empty-hint">等待可渲染的源码</p>
            </div>
          </article>
        </template>
      </ToolWorkbench>
    </section>
  </div>
</template>

<style scoped>
.mermaid-shell {
  max-width: 1280px;
}

.mermaid-panel {
  min-width: 0;
}

.mermaid-preview-header,
.mermaid-actions {
  align-items: center;
  display: flex;
  gap: 12px;
}

.mermaid-preview-header {
  justify-content: space-between;
}

.mermaid-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.mermaid-table-status {
  color: var(--brand-color-muted, var(--shell-muted));
  font-size: 0.9rem;
}

.mermaid-toolbar-block {
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-md, 16px);
  min-width: 280px;
  padding: 14px;
}

.mermaid-toolbar-save {
  flex: 1 1 100%;
}

.mermaid-source-meta {
  color: var(--brand-color-muted, var(--shell-muted));
  font-size: 0.88rem;
  margin: 12px 0 0;
}

.mermaid-toolbar-head,
.mermaid-toolbar-actions,
.mermaid-example-strip {
  display: flex;
  gap: 10px;
}

.mermaid-toolbar-head {
  align-items: center;
  justify-content: space-between;
}

.mermaid-toolbar-actions,
.mermaid-example-strip {
  flex-wrap: wrap;
  margin-top: 12px;
}

.mermaid-toolbar-sync {
  margin-top: 12px;
}

.mermaid-example-item {
  background: var(--brand-color-surface, rgba(255, 255, 255, 0.62));
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-md, 16px);
  color: var(--brand-color-text, var(--shell-navy));
  cursor: pointer;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 700;
  min-height: 32px;
  padding: 0 12px;
}

.mermaid-example-item:hover {
  background: var(--brand-color-surface-2, rgba(255, 255, 255, 0.9));
  border-color: var(--brand-color-accent, rgba(16, 37, 66, 0.18));
}

.mermaid-example-item:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.mermaid-example-item-active {
  background: var(--brand-color-accent, #102542);
  border-color: var(--brand-color-accent, #102542);
  color: var(--ui-text-inverted, #ffffff);
}

.mermaid-example-item-active:hover {
  background: var(--brand-color-accent-hover, var(--brand-color-accent, #102542));
  border-color: var(--brand-color-accent-hover, var(--brand-color-accent, #102542));
}

.mermaid-ghost-action {
  align-items: center;
  background: var(--brand-color-surface, rgba(255, 255, 255, 0.62));
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-md, 16px);
  color: var(--brand-color-text, var(--shell-navy));
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  gap: 8px;
  min-height: 38px;
  padding: 0 13px;
  text-decoration: none;
}

.mermaid-ghost-action:hover {
  background: var(--brand-color-surface-2, rgba(255, 255, 255, 0.9));
  border-color: var(--brand-color-accent, rgba(16, 37, 66, 0.18));
}

.mermaid-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.mermaid-ghost-action:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.mermaid-editor {
  display: flex;
  flex: 1 1 auto;
  min-height: 560px;
  width: 100%;
}

.mermaid-editor :deep(.mermaid-editor-base) {
  background: var(--brand-color-surface, #ffffff);
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-md, 16px);
  caret-color: var(--brand-color-accent, var(--shell-navy));
  color: var(--brand-color-text, var(--shell-ink));
  font: 0.9rem/1.65 "SFMono-Regular", "Cascadia Code", "Liberation Mono", monospace;
  height: 100%;
  margin-top: 0;
  min-height: 560px;
  outline: none;
  padding: 18px;
  resize: vertical;
  transition: border-color 120ms ease, box-shadow 120ms ease;
  width: 100%;
}

.mermaid-editor :deep(.mermaid-editor-base:focus-visible) {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
}

.mermaid-editor :deep(.mermaid-editor-base::placeholder) {
  color: var(--brand-color-muted, var(--shell-muted));
  opacity: 0.72;
}

:global(html.dark) .mermaid-editor :deep(.mermaid-editor-base),
:global(html[data-brand-theme='terminal']) .mermaid-editor :deep(.mermaid-editor-base),
:global(html[data-brand-theme='spotify']) .mermaid-editor :deep(.mermaid-editor-base) {
  background: var(--brand-color-surface-2, #0f1723);
  border-color: var(--brand-color-border, rgba(255, 255, 255, 0.08));
  color: var(--brand-color-text, #edf6ff);
}

:global(html.dark) .mermaid-editor :deep(.mermaid-editor-base::placeholder),
:global(html[data-brand-theme='terminal']) .mermaid-editor :deep(.mermaid-editor-base::placeholder),
:global(html[data-brand-theme='spotify']) .mermaid-editor :deep(.mermaid-editor-base::placeholder) {
  color: var(--brand-color-muted, rgba(237, 246, 255, 0.45));
  opacity: 0.76;
}

.mermaid-render-error {
  margin-top: 18px;
  white-space: pre-wrap;
}

.mermaid-preview-canvas {
  align-items: center;
  background: var(--brand-color-surface, #ffffff);
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-md, 16px);
  color: var(--brand-color-muted, rgba(15, 23, 35, 0.58));
  display: flex;
  flex: 1;
  justify-content: center;
  margin-top: 18px;
  min-height: 560px;
  overflow: auto;
  padding: 24px;
  text-align: center;
}

.mermaid-preview-canvas :deep(svg) {
  height: auto;
  max-height: 100%;
  max-width: 100%;
}

.mermaid-preview-empty {
  align-items: center;
  background: var(--brand-color-surface, rgba(16, 37, 66, 0.06));
  border: 1px solid var(--brand-color-border, rgba(16, 37, 66, 0.08));
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  justify-content: center;
  margin-top: 18px;
  min-height: 560px;
  padding: 24px;
}

.mermaid-empty-hint {
  color: var(--brand-color-muted, rgba(15, 23, 35, 0.6));
  font-size: 0.95rem;
  margin: 0;
}

@media (max-width: 1023px) {
  .mermaid-editor,
  .mermaid-editor :deep(.mermaid-editor-base),
  .mermaid-preview-empty,
  .mermaid-preview-canvas {
    min-height: 420px;
  }
}

@media (max-width: 599px) {
  .mermaid-preview-header,
  .mermaid-toolbar-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .mermaid-actions {
    justify-content: flex-start;
  }

  .mermaid-toolbar-block {
    min-width: 0;
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mermaid-editor :deep(.mermaid-editor-base) {
    transition: none;
  }
}
</style>
