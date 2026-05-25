<script setup>
import mermaid from 'mermaid'
import { computed, nextTick, onMounted, shallowRef, useTemplateRef, watch } from 'vue'

import AccountSyncPanel from 'src/components/tools/AccountSyncPanel.vue'
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
    description: '适合梳理产品流程、状态流转和任务路径。',
    source: defaultSource
  },
  {
    name: '时序图',
    description: '快速描述前后端、用户和第三方服务的调用关系。',
    source: `sequenceDiagram
  participant U as 用户
  participant F as 前端
  participant A as API
  U->>F: 输入 Mermaid 源码
  F->>F: 防抖渲染
  F->>A: 可选保存
  A-->>F: 返回历史记录
  F-->>U: 展示预览`
  },
  {
    name: '甘特图',
    description: '把阶段计划和交付节点放进一张轻量排期图。',
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
const actionMessage = shallowRef('')
const copied = shallowRef(false)
const rendering = shallowRef(false)
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
  return accountSync.activeItem.value ? '已加载云端版本' : accountSync.syncLabel.value
})
const activeExampleName = computed(() => {
  const activeExample = examples.find(example => example.source === source.value)
  return activeExample?.name || '自定义'
})
const previewStats = computed(() => [
  { label: '行数', value: sourceLines.value },
  { label: '字符', value: sourceCharacters.value },
  { label: '状态', value: renderStatusText.value },
  { label: '示例', value: activeExampleName.value }
])

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

async function renderDiagram() {
  const currentSequence = ++renderSequence
  rendering.value = true
  renderError.value = ''
  actionMessage.value = ''
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
  actionMessage.value = `已切换到${example.name}示例。`
}

function resetSource() {
  source.value = defaultSource
  actionMessage.value = '已恢复默认流程图示例。'
}

async function loadSyncedSource() {
  const item = await accountSync.loadItem()
  const syncedSource = item?.payload?.source
  if (typeof syncedSource === 'string' && syncedSource.trim()) {
    source.value = syncedSource
    actionMessage.value = '已读取账号同步的 Mermaid 源码。'
  } else if (accountSync.auth.authenticated) {
    actionMessage.value = '账号里还没有 Mermaid 同步内容。'
  }
}

async function saveSyncedSource() {
  const item = await accountSync.saveItem({
    title: 'Mermaid 默认图表',
    payload: {
      source: source.value,
      line_count: sourceLines.value,
      character_count: sourceCharacters.value
    }
  })
  if (item) {
    actionMessage.value = '已同步到账号。'
  }
}

async function deleteSyncedSource() {
  const deleted = await accountSync.deleteItem()
  if (deleted) {
    source.value = defaultSource
    actionMessage.value = '已删除账号同步内容，并恢复默认示例。'
  }
}

async function copySource() {
  try {
    await navigator.clipboard.writeText(source.value)
    copied.value = true
    actionMessage.value = '源码已复制到剪贴板。'
    window.setTimeout(() => {
      copied.value = false
    }, 1400)
  } catch (error) {
    actionMessage.value = formatMermaidError(error) || '复制失败，请检查浏览器剪贴板权限。'
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
    actionMessage.value = 'SVG 已开始下载。'
  } catch (error) {
    actionMessage.value = formatMermaidError(error) || '下载失败，请稍后重试。'
  }
}

watch(source, scheduleRender)

onMounted(async () => {
  configureMermaid()
  await loadSyncedSource()
  await renderDiagram()
})
</script>

<template>
  <div class="tool-detail-page mermaid-page">
    <section class="tool-detail-shell mermaid-shell">
      <div class="tool-detail-header">
        <div>
          <div class="section-kicker">Mermaid · 实时预览</div>
          <h1 class="section-title">先写清图表，再导出 SVG。</h1>
        </div>
        <p class="section-text">
          源码会在浏览器里实时渲染。登录 GitHub 后，可以把当前 Mermaid 源码同步到账号，后续继续编辑。
        </p>
      </div>

      <section class="mermaid-workspace">
        <aside class="mermaid-sidebar">
          <article class="mermaid-panel">
            <div class="mermaid-panel-topline">
              <div>
                <div class="section-kicker">示例</div>
                <h2 class="bench-title">选择图表类型</h2>
              </div>
              <span class="mermaid-limit">{{ activeExampleName }}</span>
            </div>

            <button
              v-for="example in examples"
              :key="example.name"
              class="mermaid-example-item"
              type="button"
              @click="useExample(example)"
            >
              <span class="mermaid-example-name">{{ example.name }}</span>
              <span class="mermaid-example-meta">{{ example.description }}</span>
            </button>

            <div class="mermaid-upload-actions">
              <button
                class="mermaid-primary-action"
                type="button"
                :disabled="accountSync.saving.value"
                @click="saveSyncedSource"
              >
                {{ accountSync.saving.value ? '同步中...' : accountSync.auth.authenticated ? '同步到账号' : '登录后同步' }}
              </button>
              <button
                class="mermaid-ghost-action"
                type="button"
                @click="resetSource"
              >
                重置示例
              </button>
            </div>
            <p class="mermaid-helper">
              示例只会替换当前编辑器内容。保存到账号后，后续可以从云端读取回来继续编辑。
            </p>
            <AccountSyncPanel
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              description="登录后可把当前 Mermaid 源码同步到账号，并在其他设备继续编辑。"
              @login="accountSync.login"
            />
          </article>

          <article
            v-if="!accountSync.auth.initialized || accountSync.auth.loading"
            class="mermaid-panel mermaid-sync-panel"
          >
            <div class="section-kicker">登录状态</div>
            <h2 class="bench-title">正在检查 GitHub 登录</h2>
            <p class="mermaid-helper">
              预览和导出功能可直接使用，登录状态只影响账号同步。
            </p>
          </article>

          <article
            v-else-if="!accountSync.auth.authenticated"
            class="mermaid-panel mermaid-sync-panel"
          >
            <div class="section-kicker">同步</div>
            <h2 class="bench-title">登录后启用源码同步</h2>
            <p class="mermaid-helper">
              同步内容会绑定到你的 GitHub 账号，当前版本保留一份默认 Mermaid 草稿。
            </p>
            <button
              class="mermaid-primary-action mermaid-auth-action"
              type="button"
              :disabled="accountSync.auth.loading"
              @click="accountSync.login"
            >
              {{ accountSync.auth.loading ? '正在跳转...' : '使用 GitHub 登录' }}
            </button>
          </article>

          <article
            v-else
            class="mermaid-panel mermaid-sync-panel"
          >
            <div class="mermaid-panel-topline">
              <div>
                <div class="section-kicker">同步</div>
                <h2 class="bench-title">账号草稿</h2>
              </div>
              <button
                class="mermaid-ghost-action"
                type="button"
                :disabled="accountSync.loading.value"
                @click="loadSyncedSource"
              >
                {{ accountSync.loading.value ? '读取中' : '读取云端' }}
              </button>
            </div>
            <div
              v-if="!accountSync.activeItem.value"
              class="mermaid-empty"
            >
              还没有 Mermaid 同步内容。
            </div>
            <div
              v-else
              class="mermaid-sync-item"
            >
              <span class="mermaid-sync-name">{{ accountSync.activeItem.value.title || 'Mermaid 默认图表' }}</span>
              <span class="mermaid-sync-meta">{{ syncStatusText }}</span>
            </div>
            <button
              class="mermaid-ghost-action mermaid-danger-action mermaid-sync-delete"
              type="button"
              :disabled="!accountSync.activeItem.value || accountSync.deleting.value"
              @click="deleteSyncedSource"
            >
              {{ accountSync.deleting.value ? '删除中' : '删除云端' }}
            </button>
          </article>
        </aside>

        <main class="mermaid-main">
          <div
            v-if="accountSync.errorMessage.value"
            class="csv-notice csv-notice-error"
          >
            {{ accountSync.errorMessage.value }}
          </div>
          <div
            v-if="actionMessage"
            class="csv-notice"
          >
            {{ actionMessage }}
          </div>

          <article class="mermaid-panel mermaid-editor-panel">
            <div class="mermaid-preview-header">
              <div>
                <div class="section-kicker">源码</div>
                <h2 class="mermaid-file-title">Mermaid 编辑器</h2>
              </div>
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

            <div class="mermaid-summary-grid">
              <div
                v-for="item in previewStats"
                :key="item.label"
                class="mermaid-summary-card"
              >
                <div class="mermaid-summary-value">{{ item.value }}</div>
                <div class="mermaid-summary-label">{{ item.label }}</div>
              </div>
            </div>
          </article>

          <article
            class="mermaid-panel mermaid-preview-panel"
          >
            <div class="mermaid-preview-header">
              <div>
                <div class="section-kicker">预览</div>
                <h2 class="mermaid-file-title">实时图表</h2>
              </div>
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
              <div class="section-kicker">预览</div>
              <h2 class="content-title">输入 Mermaid 源码</h2>
              <p class="section-text">
                右侧会显示渲染结果。空内容不会触发 Mermaid 解析。
              </p>
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
              <div class="section-kicker">预览</div>
              <h2 class="content-title">等待可渲染的图表源码</h2>
              <p class="section-text">
                修正语法后，预览会自动恢复。
              </p>
            </div>
          </article>
        </main>
      </section>
    </section>
  </div>
</template>

<style scoped>
.mermaid-shell {
  max-width: 1280px;
}

.mermaid-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
  padding: 22px;
}

.mermaid-workspace {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(280px, 0.35fr) minmax(0, 0.65fr);
  margin-top: 28px;
}

.mermaid-sidebar,
.mermaid-main {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.mermaid-panel-topline,
.mermaid-preview-header,
.mermaid-actions {
  align-items: center;
  display: flex;
  gap: 12px;
}

.mermaid-panel-topline,
.mermaid-preview-header {
  justify-content: space-between;
}

.mermaid-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.mermaid-limit,
.mermaid-helper,
.mermaid-example-meta,
.mermaid-empty,
.mermaid-sync-meta,
.mermaid-table-status {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.mermaid-example-item,
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
  width: 100%;
}

.mermaid-example-item {
  cursor: pointer;
  margin-top: 12px;
}

.mermaid-example-item:hover {
  border-color: rgba(16, 37, 66, 0.18);
}

.mermaid-example-name,
.mermaid-sync-name,
.mermaid-file-title {
  color: var(--shell-navy);
  font-weight: 800;
}

.mermaid-file-title {
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.4rem, 2.5vw, 2rem);
  margin: 8px 0 0;
  overflow-wrap: anywhere;
}

.mermaid-upload-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.mermaid-primary-action {
  background: var(--brand-color-accent, #102542);
  border: 0;
  border-radius: var(--brand-radius-pill, 999px);
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 800;
  min-height: 46px;
  padding: 0 18px;
}

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

.mermaid-ghost-action:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.mermaid-primary-action:disabled,
.mermaid-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.mermaid-auth-action,
.mermaid-sync-delete {
  margin-top: 16px;
  width: 100%;
}

.mermaid-danger-action {
  color: #9b2f25;
}

.mermaid-helper {
  line-height: 1.6;
  margin: 14px 0 0;
}

.mermaid-sync-panel {
  max-height: 560px;
  overflow: auto;
}

.mermaid-empty {
  background: rgba(255, 255, 255, 0.54);
  border: 1px dashed rgba(16, 37, 66, 0.16);
  border-radius: var(--brand-radius-md, 16px);
  margin-top: 14px;
  padding: 16px;
}

.mermaid-sync-item {
  margin-top: 14px;
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

.mermaid-summary-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 18px;
}

.mermaid-summary-card {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line);
  border-radius: 18px;
  padding: 16px;
  min-width: 0;
}

.mermaid-summary-value {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.1rem, 2.2vw, 1.8rem);
  font-weight: 700;
  overflow-wrap: anywhere;
}

.mermaid-summary-label {
  color: rgba(15, 23, 35, 0.6);
  font-size: 0.88rem;
  margin-top: 6px;
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
  background: rgba(16, 37, 66, 0.06);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  margin-top: 18px;
  min-height: 340px;
  padding: 24px;
}

@media (max-width: 1023px) {
  .mermaid-workspace {
    grid-template-columns: 1fr;
  }

  .mermaid-summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .mermaid-editor,
  .mermaid-preview-canvas {
    min-height: 420px;
  }
}

@media (max-width: 599px) {
  .mermaid-panel {
    padding: 18px;
  }

  .mermaid-preview-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .mermaid-actions {
    justify-content: flex-start;
  }

  .mermaid-summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
