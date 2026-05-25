<script setup>
import mermaid from 'mermaid'
import { computed, nextTick, onMounted, shallowRef, useTemplateRef, watch } from 'vue'

import AccountSyncPanel from 'src/components/tools/AccountSyncPanel.vue'
import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import ToolWorkbench from 'src/components/tools/ToolWorkbench.vue'
import { useAccountSync } from 'src/composables/useAccountSync'

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
const deletingArchiveKey = shallowRef('')
const previewRef = useTemplateRef('preview')
const accountSync = useAccountSync('mermaid')

let renderTimer = 0
let renderSequence = 0

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
const syncStatusText = computed(() => {
  if (accountSync.saving.value) return '正在同步'
  if (accountSync.loading.value) return '正在读取云端'
  return accountSync.items.value.length ? `${accountSync.items.value.length} 个云端存档` : accountSync.syncLabel.value
})
const activeExampleName = computed(() => {
  const activeExample = examples.find(example => example.source === source.value)
  return activeExample?.name || '自定义'
})
const sourceMetaText = computed(() => [
  `${sourceLines.value} 行`,
  `${sourceCharacters.value} 字符`,
  renderStatusText.value,
  `示例：${activeExampleName.value}`
].join(' · '))

function configureMermaid() {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'base',
    themeVariables: {
      primaryColor: '#eef6ff',
      primaryTextColor: '#102542',
      primaryBorderColor: '#7fb2d9',
      lineColor: '#47627f',
      secondaryColor: '#fff7ed',
      tertiaryColor: '#f7fbff',
      fontFamily: 'Avenir Next, Segoe UI, sans-serif'
    }
  })
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

function formatArchiveDate(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function createArchiveKey() {
  const timestamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)
  const suffix = Math.random().toString(36).slice(2, 8)
  return `archive-${timestamp}-${suffix}`
}

function createArchiveTitle() {
  return `Mermaid 图表 ${formatArchiveDate(new Date())}`
}

function createArchivePayload(itemKey) {
  return {
    source: source.value,
    line_count: sourceLines.value,
    character_count: sourceCharacters.value,
    archive_key: itemKey,
    updated_from: 'mermaid-editor'
  }
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
    result.bindFunctions?.(previewRef.value)
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

function openArchive(item) {
  const syncedSource = item?.payload?.source
  if (typeof syncedSource === 'string' && syncedSource.trim()) {
    accountSync.activeItem.value = item
    source.value = syncedSource
    actionError.value = ''
  } else {
    actionError.value = '存档源码为空'
  }
}

async function persistSyncedSource({ forceNew = false } = {}) {
  const activeItemKey = accountSync.activeItem.value?.item_key
  const nextItemKey = forceNew || !activeItemKey ? createArchiveKey() : activeItemKey
  const isNewArchive = nextItemKey !== activeItemKey
  const item = await accountSync.saveItem({
    title: isNewArchive ? createArchiveTitle() : accountSync.activeItem.value?.title || createArchiveTitle(),
    nextItemKey,
    payload: createArchivePayload(nextItemKey)
  })
  if (item) actionError.value = ''
}

async function saveSyncedSource() {
  await persistSyncedSource()
}

async function saveSyncedSourceAsNew() {
  await persistSyncedSource({ forceNew: true })
}

async function deleteSyncedSource(item) {
  if (!item?.item_key) return

  deletingArchiveKey.value = item.item_key
  const deleted = await accountSync.deleteItem(item.item_key)
  if (deleted) {
    if (accountSync.activeItem.value?.item_key === item.item_key) {
      accountSync.activeItem.value = null
    }
    actionError.value = ''
  }
  deletingArchiveKey.value = ''
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
  await accountSync.loadItems()
  await renderDiagram()
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
              <span class="mermaid-table-status">{{ syncStatusText }}</span>
            </div>

            <p class="mermaid-source-meta">{{ sourceMetaText }}</p>

            <div class="mermaid-toolbar-actions">
              <button
                class="mermaid-primary-action"
                type="button"
                :disabled="accountSync.saving.value"
                @click="saveSyncedSource"
              >
                {{ accountSync.saving.value ? '保存中...' : accountSync.auth.authenticated ? '保存' : '登录后保存' }}
              </button>
              <button
                class="mermaid-ghost-action"
                type="button"
                :disabled="accountSync.saving.value"
                @click="saveSyncedSourceAsNew"
              >
                另存为新存档
              </button>
              <button
                class="mermaid-ghost-action"
                type="button"
                @click="resetSource"
              >
                重置示例
              </button>
            </div>

            <div class="mermaid-example-strip">
              <button
                v-for="example in examples"
                :key="example.name"
                class="mermaid-example-item"
                :class="{ 'mermaid-example-item-active': activeExampleName === example.name }"
                type="button"
                @click="useExample(example)"
              >
                {{ example.name }}
              </button>
            </div>

            <AccountSyncPanel
              class="mermaid-toolbar-sync"
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              @login="accountSync.login"
            />
          </section>

          <section class="mermaid-toolbar-block mermaid-toolbar-archive">
            <div class="mermaid-toolbar-head">
              <div class="section-kicker">历史</div>
              <button
                class="mermaid-ghost-action"
                type="button"
                :disabled="accountSync.loading.value"
                @click="accountSync.loadItems"
              >
                {{ accountSync.loading.value ? '刷新中' : '刷新' }}
              </button>
            </div>

            <div
              v-if="!accountSync.auth.initialized || accountSync.auth.loading"
              class="mermaid-toolbar-empty"
            >
              检查登录中
            </div>
            <div
              v-else-if="!accountSync.auth.authenticated"
              class="mermaid-toolbar-empty"
            >
              未登录
            </div>
            <div
              v-else-if="!accountSync.items.value.length && !accountSync.loading.value"
              class="mermaid-toolbar-empty"
            >
              无存档
            </div>
            <div
              v-else
              class="mermaid-archive-strip"
            >
            <div
              v-for="item in accountSync.items.value"
              :key="item.item_key"
              class="mermaid-archive-row"
            >
              <button
                class="mermaid-sync-item"
                :class="{ 'mermaid-sync-item-active': accountSync.activeItem.value?.item_key === item.item_key }"
                type="button"
                @click="openArchive(item)"
              >
                <span class="mermaid-sync-name">{{ item.title || 'Mermaid 图表' }}</span>
                <span class="mermaid-sync-meta">
                  {{ item.payload?.character_count || 0 }} 字符 · {{ formatArchiveDate(item.updated_at) }}
                </span>
              </button>
              <button
                class="mermaid-ghost-action mermaid-danger-action mermaid-archive-delete"
                type="button"
                :disabled="deletingArchiveKey === item.item_key"
                @click="deleteSyncedSource(item)"
              >
                {{ deletingArchiveKey === item.item_key ? '删除中' : '删除' }}
              </button>
            </div>
            </div>
          </section>
        </template>

        <template #source>
          <div
            v-if="accountSync.errorMessage.value"
            class="csv-notice csv-notice-error"
          >
            {{ accountSync.errorMessage.value }}
          </div>
          <div
            v-if="actionError"
            class="csv-notice csv-notice-error"
          >
            {{ actionError }}
          </div>

          <article class="mermaid-panel mermaid-editor-panel">
            <div class="mermaid-preview-header">
              <div class="mermaid-actions">
                <button
                  class="mermaid-ghost-action"
                  type="button"
                  @click="copySource"
                >
                  {{ copied ? '已复制' : '复制源码' }}
                </button>
                <button
                  class="mermaid-ghost-action"
                  type="button"
                  :disabled="!canDownload"
                  @click="downloadSvg"
                >
                  下载 SVG
                </button>
              </div>
            </div>

            <textarea
              v-model="source"
              class="mermaid-editor"
              spellcheck="false"
              aria-label="Mermaid source"
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

.mermaid-sync-meta,
.mermaid-toolbar-empty,
.mermaid-table-status {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.mermaid-toolbar-block {
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  min-width: 280px;
  padding: 14px;
}

.mermaid-toolbar-save {
  flex: 1.1 1 420px;
}

.mermaid-toolbar-archive {
  flex: 1 1 360px;
}

.mermaid-source-meta {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
  margin: 12px 0 0;
}

.mermaid-toolbar-head,
.mermaid-toolbar-actions,
.mermaid-example-strip,
.mermaid-archive-strip {
  display: flex;
  gap: 10px;
}

.mermaid-toolbar-head {
  align-items: center;
  justify-content: space-between;
}

.mermaid-toolbar-actions,
.mermaid-example-strip,
.mermaid-archive-strip {
  flex-wrap: wrap;
  margin-top: 12px;
}

.mermaid-toolbar-sync {
  margin-top: 12px;
}

.mermaid-toolbar-empty {
  background: rgba(255, 255, 255, 0.54);
  border: 1px dashed rgba(16, 37, 66, 0.16);
  border-radius: var(--brand-radius-md, 16px);
  margin-top: 12px;
  padding: 12px;
}

.mermaid-sync-item {
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  text-align: left;
  width: min(260px, 100%);
  cursor: pointer;
}

.mermaid-example-item {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  cursor: pointer;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 700;
  min-height: 32px;
  padding: 0 12px;
}

.mermaid-example-item:hover {
  border-color: rgba(16, 37, 66, 0.18);
}

.mermaid-example-item:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.mermaid-example-item-active {
  background: rgba(16, 37, 66, 0.08);
  border-color: var(--brand-color-accent, #102542);
}

.mermaid-sync-name {
  color: var(--shell-navy);
  font-weight: 800;
}

.mermaid-primary-action,
.mermaid-ghost-action {
  align-items: center;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
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

.mermaid-primary-action {
  background: var(--brand-color-accent, #102542);
  border-color: var(--brand-color-accent, #102542);
  color: #ffffff;
}

.mermaid-ghost-action:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.mermaid-primary-action:disabled,
.mermaid-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.mermaid-danger-action {
  color: #9b2f25;
}

.mermaid-archive-row {
  align-items: stretch;
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(0, 1fr) auto;
  width: min(360px, 100%);
}

.mermaid-sync-item-active {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
}

.mermaid-archive-delete {
  align-self: center;
}

.mermaid-editor {
  background: #0f1723;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  color: #edf6ff;
  font: 0.95rem/1.65 "SFMono-Regular", "Cascadia Code", "Liberation Mono", monospace;
  margin-top: 16px;
  min-height: 520px;
  outline: none;
  padding: 18px;
  resize: vertical;
  width: 100%;
}

.mermaid-editor:focus {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
}

.mermaid-render-error {
  margin-top: 18px;
  white-space: pre-wrap;
}

.mermaid-preview-canvas {
  align-items: center;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(247, 251, 255, 0.76));
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: rgba(15, 23, 35, 0.58);
  display: flex;
  flex: 1;
  justify-content: center;
  margin-top: 16px;
  min-height: 520px;
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
  background: rgba(16, 37, 66, 0.06);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  justify-content: center;
  margin-top: 18px;
  min-height: 340px;
  padding: 24px;
}

.mermaid-empty-hint {
  color: rgba(15, 23, 35, 0.6);
  font-size: 0.95rem;
  margin: 0;
}

@media (max-width: 1023px) {
  .mermaid-editor,
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

  .mermaid-archive-row {
    grid-template-columns: 1fr;
  }

  .mermaid-archive-delete {
    align-self: stretch;
  }

  .mermaid-toolbar-block {
    min-width: 0;
    width: 100%;
  }
}
</style>
