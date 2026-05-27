<script setup>
import mermaid from 'mermaid'
import { computed, nextTick, onMounted, onUnmounted, shallowRef, useTemplateRef, watch } from 'vue'

import AccountSyncPanel from 'src/components/tools/AccountSyncPanel.vue'
import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import ToolSaveDialog from 'src/components/tools/ToolSaveDialog.vue'
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
const historyOpen = shallowRef(false)
const previewRef = useTemplateRef('preview')
const accountSync = useAccountSync('mermaid')
const saveDialogOpen = shallowRef(false)
const saveDialogMode = shallowRef('save')
const saveDialogDefaults = shallowRef({ title: '', remark: '' })

let renderTimer = 0
let renderSequence = 0
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
const syncStatusText = computed(() => {
  if (accountSync.saving.value) return '同步中'
  if (accountSync.loading.value) return '读取中'
  return ''
})
const archiveCountText = computed(() => {
  if (accountSync.loading.value) return '读取中'
  return accountSync.items.value.length ? String(accountSync.items.value.length) : ''
})
const historyTriggerLabel = computed(() => {
  if (!accountSync.auth.initialized || accountSync.auth.loading) return '检查登录中'
  if (!accountSync.auth.authenticated) return '未登录 · 登录后同步'
  if (accountSync.loading.value) return '读取中'
  const active = accountSync.activeItem.value
  if (active) {
    const activeLabel = (active.title || '').trim() || formatArchiveDate(active.updated_at)
    return `历史 · ${activeLabel}`
  }
  if (!accountSync.items.value.length) return '无存档'
  return `历史存档 · ${accountSync.items.value.length}`
})
const historyTriggerDisabled = computed(() => {
  if (!accountSync.auth.initialized || accountSync.auth.loading) return true
  if (!accountSync.auth.authenticated) return true
  if (accountSync.loading.value) return false
  return !accountSync.items.value.length
})
const activeExampleName = computed(() => {
  const activeExample = examples.find(example => example.source === source.value)
  return activeExample?.name || '自定义'
})
const sourceMetaText = computed(() => [
  `${sourceLines.value} 行`,
  `${sourceCharacters.value} 字符`
].join(' · '))

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
    configureMermaid()
    renderDiagram()
  })
  themeObserver.observe(document.documentElement, {
    attributeFilter: ['class', 'data-brand-theme'],
    attributes: true
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

function createArchivePayload(itemKey, { remark = '' } = {}) {
  return {
    source: source.value,
    line_count: sourceLines.value,
    character_count: sourceCharacters.value,
    archive_key: itemKey,
    updated_from: 'mermaid-editor',
    remark: remark || ''
  }
}

function archiveDisplayTitle(item) {
  return (item?.title || '').trim() || `Mermaid 图表 ${formatArchiveDate(item.updated_at)}`
}

function archiveSecondaryLine(item) {
  const remark = (item?.payload?.remark || '').trim()
  const stamp = formatArchiveDate(item.updated_at)
  return remark ? `${remark} · ${stamp}` : stamp
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
    historyOpen.value = false
  } else {
    actionError.value = '存档源码为空'
  }
}

async function persistSyncedSource({ forceNew = false, title = '', remark = '' } = {}) {
  const activeItemKey = accountSync.activeItem.value?.item_key
  const nextItemKey = forceNew || !activeItemKey ? createArchiveKey() : activeItemKey
  const isNewArchive = nextItemKey !== activeItemKey
  const trimmedTitle = (title || '').trim()
  const fallbackTitle = isNewArchive
    ? createArchiveTitle()
    : accountSync.activeItem.value?.title || createArchiveTitle()
  const item = await accountSync.saveItem({
    title: trimmedTitle || fallbackTitle,
    nextItemKey,
    payload: createArchivePayload(nextItemKey, { remark })
  })
  if (item) actionError.value = ''
}

function openSaveDialog(mode = 'save') {
  saveDialogMode.value = mode
  if (mode === 'save') {
    const active = accountSync.activeItem.value
    saveDialogDefaults.value = {
      title: active?.title || '',
      remark: active?.payload?.remark || ''
    }
  } else {
    saveDialogDefaults.value = { title: '', remark: '' }
  }
  saveDialogOpen.value = true
}

async function saveSyncedSource() {
  if (!accountSync.auth.authenticated) {
    const authenticated = await accountSync.ensureAuth()
    if (!authenticated) {
      accountSync.login()
      return
    }
  }
  openSaveDialog('save')
}

async function saveSyncedSourceAsNew() {
  if (!accountSync.auth.authenticated) {
    const authenticated = await accountSync.ensureAuth()
    if (!authenticated) {
      accountSync.login()
      return
    }
  }
  openSaveDialog('save-as-new')
}

async function handleSaveDialogConfirm({ title, remark }) {
  await persistSyncedSource({
    forceNew: saveDialogMode.value === 'save-as-new',
    title,
    remark
  })
  saveDialogOpen.value = false
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
  watchThemeChanges()
  await accountSync.loadItems()
  await renderDiagram()
})

onUnmounted(() => {
  window.clearTimeout(renderTimer)
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
                v-if="syncStatusText"
                class="mermaid-table-status"
              >{{ syncStatusText }}</span>
            </div>

            <p class="mermaid-source-meta">{{ sourceMetaText }}</p>

            <div class="mermaid-toolbar-actions">
              <UButton
                class="mermaid-primary-action brand-action-button"
                color="primary"
                :label="accountSync.auth.authenticated ? '保存' : '登录后保存'"
                :loading="accountSync.saving.value"
                type="button"
                :disabled="accountSync.saving.value"
                @click="saveSyncedSource"
              />
              <UButton
                class="mermaid-ghost-action"
                color="neutral"
                label="另存为新存档"
                type="button"
                variant="subtle"
                :disabled="accountSync.saving.value"
                @click="saveSyncedSourceAsNew"
              />
              <UButton
                class="mermaid-ghost-action"
                color="neutral"
                label="重置示例"
                type="button"
                variant="subtle"
                @click="resetSource"
              />

              <UPopover
                v-model:open="historyOpen"
                :content="{ align: 'end', sideOffset: 8 }"
              >
                <UButton
                  class="mermaid-ghost-action mermaid-history-trigger"
                  color="neutral"
                  type="button"
                  variant="subtle"
                  :disabled="historyTriggerDisabled"
                  aria-label="历史存档"
                >
                  <span>{{ historyTriggerLabel }}</span>
                  <span
                    class="mermaid-history-trigger-caret"
                    aria-hidden="true"
                  >▾</span>
                </UButton>

                <template #content>
                  <div class="mermaid-history-popover">
                    <div class="mermaid-history-popover-head">
                      <div class="mermaid-toolbar-head-left">
                        <div class="section-kicker">历史</div>
                        <span
                          v-if="archiveCountText"
                          class="mermaid-archive-count"
                        >· {{ archiveCountText }}</span>
                      </div>
                      <UButton
                        class="mermaid-ghost-action mermaid-history-refresh"
                        color="neutral"
                        :label="accountSync.loading.value ? '刷新中' : '刷新'"
                        :loading="accountSync.loading.value"
                        size="sm"
                        type="button"
                        variant="subtle"
                        :disabled="accountSync.loading.value"
                        @click="accountSync.loadItems"
                      />
                    </div>

                    <div
                      v-if="accountSync.loading.value && !accountSync.items.value.length"
                      class="mermaid-history-popover-empty"
                    >
                      读取中
                    </div>
                    <div
                      v-else-if="!accountSync.items.value.length"
                      class="mermaid-history-popover-empty"
                    >
                      无存档
                    </div>
                    <div
                      v-else
                      class="mermaid-archive-list"
                    >
                      <div
                        v-for="item in accountSync.items.value"
                        :key="item.item_key"
                        class="mermaid-archive-row"
                        :class="{ 'mermaid-archive-row-active': accountSync.activeItem.value?.item_key === item.item_key }"
                      >
                        <UButton
                          class="mermaid-archive-open"
                          color="neutral"
                          type="button"
                          variant="ghost"
                          @click="openArchive(item)"
                        >
                          <span class="mermaid-archive-title">{{ archiveDisplayTitle(item) }}</span>
                          <span class="mermaid-archive-meta">{{ archiveSecondaryLine(item) }}</span>
                        </UButton>
                        <UButton
                          class="mermaid-archive-delete"
                          color="error"
                          :label="deletingArchiveKey === item.item_key ? '...' : '×'"
                          size="xs"
                          type="button"
                          variant="ghost"
                          :disabled="deletingArchiveKey === item.item_key"
                          :aria-label="`删除 ${archiveDisplayTitle(item)}`"
                          @click.stop="deleteSyncedSource(item)"
                        />
                      </div>
                    </div>
                  </div>
                </template>
              </UPopover>

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

            <AccountSyncPanel
              class="mermaid-toolbar-sync"
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              @login="accountSync.login"
            />
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

      <ToolSaveDialog
        v-model:open="saveDialogOpen"
        :default-title="saveDialogDefaults.title"
        :default-remark="saveDialogDefaults.remark"
        :busy="accountSync.saving.value"
        :dialog-title="saveDialogMode === 'save-as-new' ? '另存为新存档' : '保存到云端存档'"
        @confirm="handleSaveDialogConfirm"
      />
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

.mermaid-history-trigger {
  display: inline-flex;
  max-width: 320px;
}

.mermaid-history-trigger > span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mermaid-history-trigger-caret {
  font-size: 0.78rem;
  margin-left: 2px;
}

.mermaid-history-refresh {
  min-height: 32px;
  padding: 0 10px;
  font-size: 0.82rem;
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

.mermaid-toolbar-head-left {
  align-items: baseline;
  display: flex;
  gap: 6px;
}

.mermaid-archive-count {
  color: var(--brand-color-muted, var(--shell-muted));
  font-size: 0.88rem;
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
  border-radius: var(--brand-radius-pill, 999px);
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

.mermaid-primary-action,
.mermaid-ghost-action {
  align-items: center;
  background: var(--brand-color-surface, rgba(255, 255, 255, 0.62));
  border: 1px solid var(--brand-color-border, var(--shell-line));
  border-radius: var(--brand-radius-pill, 999px);
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

.mermaid-primary-action {
  background: var(--brand-color-accent, #102542);
  border-color: var(--brand-color-accent, #102542);
  color: var(--ui-text-inverted, #ffffff);
}

.mermaid-ghost-action:hover {
  background: var(--brand-color-surface-2, rgba(255, 255, 255, 0.9));
  border-color: var(--brand-color-accent, rgba(16, 37, 66, 0.18));
}

.mermaid-primary-action:disabled,
.mermaid-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.mermaid-primary-action:focus-visible,
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

<style>
.mermaid-history-popover {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  color: var(--shell-navy, #102542);
  min-width: 320px;
  padding: 12px;
  z-index: 90;
}

.mermaid-history-popover:focus-visible {
  outline: none;
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.mermaid-history-popover-head {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.mermaid-history-popover-empty {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
  margin-top: 10px;
  padding: 6px 4px;
}

.mermaid-archive-list {
  background: #ffffff;
  border: 1px solid var(--shell-line, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-md, 16px);
  display: flex;
  flex-direction: column;
  margin-top: 12px;
  max-height: min(60vh, 360px);
  overflow-y: auto;
  scrollbar-color: rgba(16, 37, 66, 0.24) transparent;
  scrollbar-width: thin;
}

.mermaid-archive-list::-webkit-scrollbar {
  width: 8px;
}

.mermaid-archive-list::-webkit-scrollbar-thumb {
  background: rgba(16, 37, 66, 0.2);
  border-radius: 999px;
}

.mermaid-archive-row {
  align-items: center;
  background: transparent;
  border-top: 1px solid rgba(16, 37, 66, 0.06);
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(0, 1fr) auto;
  min-height: 32px;
  padding: 4px 8px 4px 10px;
  position: relative;
  transition: background 120ms ease;
}

.mermaid-archive-row:first-child {
  border-top: 0;
}

.mermaid-archive-row:hover,
.mermaid-archive-row:focus-within {
  background: rgba(16, 37, 66, 0.04);
}

.mermaid-archive-row-active {
  background: rgba(16, 37, 66, 0.06);
  box-shadow: inset 3px 0 0 0 var(--brand-color-accent, #102542);
}

.mermaid-archive-open {
  align-items: flex-start;
  background: transparent;
  border: 0;
  color: inherit;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  font: inherit;
  gap: 2px;
  min-height: 28px;
  min-width: 0;
  padding: 2px 0;
  text-align: left;
  width: 100%;
}

.mermaid-archive-open:focus-visible {
  border-radius: var(--brand-radius-sm, 8px);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.mermaid-archive-title {
  color: var(--shell-navy, #102542);
  font-size: 0.88rem;
  font-weight: 700;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mermaid-archive-meta {
  color: rgba(15, 23, 35, 0.55);
  font-size: 0.8rem;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mermaid-archive-delete {
  align-items: center;
  background: transparent;
  border: 0;
  border-radius: var(--brand-radius-pill, 999px);
  color: rgba(15, 23, 35, 0.4);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 1.05rem;
  font-weight: 700;
  height: 24px;
  justify-content: center;
  line-height: 1;
  padding: 0;
  transition: color 120ms ease, background 120ms ease;
  width: 24px;
}

.mermaid-archive-row:hover .mermaid-archive-delete,
.mermaid-archive-row:focus-within .mermaid-archive-delete {
  color: var(--shell-coral, #ff7a59);
}

.mermaid-archive-delete:hover {
  background: rgba(255, 122, 89, 0.12);
  color: var(--shell-coral, #ff7a59);
}

.mermaid-archive-delete:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  color: var(--shell-coral, #ff7a59);
  outline: none;
}

.mermaid-archive-delete:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
