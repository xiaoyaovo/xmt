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
}

function resetSource() {
  source.value = defaultSource
  actionMessage.value = '已恢复默认流程图示例。'
}

function openArchive(item) {
  const syncedSource = item?.payload?.source
  if (typeof syncedSource === 'string' && syncedSource.trim()) {
    accountSync.activeItem.value = item
    source.value = syncedSource
    actionMessage.value = '已载入 Mermaid 云端存档。'
  } else {
    actionMessage.value = '这个存档没有可读取的 Mermaid 源码。'
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
  if (item) {
    actionMessage.value = isNewArchive ? '已另存为 Mermaid 云端存档。' : '已保存当前 Mermaid 云端存档。'
  }
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
    actionMessage.value = '已删除 Mermaid 云端存档。'
  }
  deletingArchiveKey.value = ''
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
  await accountSync.loadItems()
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
      </div>

      <section class="mermaid-workspace">
        <aside class="mermaid-sidebar">
          <article class="mermaid-panel">
            <div class="mermaid-panel-topline">
              <div>
                <div class="section-kicker">示例</div>
                <h2 class="bench-title">选择图表类型</h2>
              </div>
              <span class="mermaid-limit">{{ syncStatusText }}</span>
            </div>

            <button
              v-for="example in examples"
              :key="example.name"
              class="mermaid-example-item"
              :class="{ 'mermaid-example-item-active': activeExampleName === example.name }"
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
            <p class="mermaid-helper">
              保存会更新当前打开的云端存档；未打开存档时会创建第一条。需要保留副本时使用另存为新存档。
            </p>
            <AccountSyncPanel
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              description="登录后可把当前 Mermaid 源码保存为账号存档，并在其他设备继续编辑。"
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
              可以保存当前 Mermaid 源码，也可以另存为新存档来保留不同图表或不同版本。
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
                <h2 class="bench-title">云端存档</h2>
              </div>
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
              v-if="!accountSync.items.value.length"
              class="mermaid-empty"
            >
              还没有 Mermaid 云端存档。
            </div>
            <template v-else>
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
            </template>
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
                预览区会显示渲染结果。空内容不会触发 Mermaid 解析。
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

.mermaid-example-item-active {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
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

.mermaid-auth-action {
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

.mermaid-archive-row {
  align-items: stretch;
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(0, 1fr) auto;
  margin-top: 12px;
}

.mermaid-sync-item {
  cursor: pointer;
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

  .mermaid-archive-row {
    grid-template-columns: 1fr;
  }

  .mermaid-archive-delete {
    align-self: stretch;
  }
}
</style>
