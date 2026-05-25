<script setup>
import {
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger
} from 'reka-ui'
import { computed, onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue'

import AccountSyncPanel from 'src/components/tools/AccountSyncPanel.vue'
import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import ToolSaveDialog from 'src/components/tools/ToolSaveDialog.vue'
import { useAccountSync } from 'src/composables/useAccountSync'

const drawioOrigin = 'https://embed.diagrams.net'
const drawioUrl = `${drawioOrigin}/?embed=1&proto=json&spin=1&ui=min&libraries=1&saveAndExit=0&noSaveBtn=0&noExitBtn=1`
const starterXml = `<mxfile host="xinming-tools" modified="2026-05-25T00:00:00.000Z" agent="Xinming Tools" version="30.0.2">
  <diagram id="xinming-demo" name="Demo">
    <mxGraphModel dx="1120" dy="680" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="start" value="Xinming Tools" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#eef6ff;strokeColor=#7fb2d9;fontColor=#102542;" vertex="1" parent="1">
          <mxGeometry x="120" y="180" width="160" height="70" as="geometry" />
        </mxCell>
        <mxCell id="edit" value="Draw.io iframe" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff7ed;strokeColor=#ffb06b;fontColor=#102542;" vertex="1" parent="1">
          <mxGeometry x="390" y="180" width="170" height="70" as="geometry" />
        </mxCell>
        <mxCell id="save" value="postMessage 保存 XML" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f2ffe1;strokeColor=#9fce54;fontColor=#102542;" vertex="1" parent="1">
          <mxGeometry x="690" y="180" width="190" height="70" as="geometry" />
        </mxCell>
        <mxCell id="edge-start-edit" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#47627f;" edge="1" parent="1" source="start" target="edit">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="edge-edit-save" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#47627f;" edge="1" parent="1" source="edit" target="save">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`

const iframeRef = useTemplateRef('drawioFrame')
const savedXml = shallowRef(starterXml)
const editorReady = shallowRef(false)
const drawioError = shallowRef('')
const savedAt = shallowRef('')
const iframeKey = shallowRef(0)
const syncAfterNextExport = shallowRef(false)
const syncingExport = shallowRef(false)
const deletingArchiveKey = shallowRef('')
const historyOpen = shallowRef(false)
const accountSync = useAccountSync('drawio')
const saveDialogOpen = shallowRef(false)
const saveDialogDefaults = shallowRef({ title: '', remark: '' })
const pendingArchiveMeta = shallowRef({ title: '', remark: '' })

const xmlCharacters = computed(() => savedXml.value.length)
const syncStatusText = computed(() => {
  if (syncingExport.value) return '准备同步'
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
const syncButtonText = computed(() => {
  if (syncingExport.value) return '准备保存...'
  if (accountSync.saving.value) return '保存中...'
  return accountSync.auth.authenticated ? '保存' : '登录后保存'
})
const syncButtonDisabled = computed(() => syncingExport.value || accountSync.saving.value)
const editorMetaText = computed(() => {
  const parts = [`${xmlCharacters.value} 字符`]
  if (savedAt.value) parts.push(`已保存 ${savedAt.value}`)
  return parts.join(' · ')
})

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
  return `Draw.io 图表 ${formatArchiveDate(new Date())}`
}

function archiveDisplayTitle(item) {
  return (item?.title || '').trim() || `Draw.io 图表 ${formatArchiveDate(item.updated_at)}`
}

function archiveSecondaryLine(item) {
  const remark = (item?.payload?.remark || '').trim()
  const stamp = formatArchiveDate(item.updated_at)
  return remark ? `${remark} · ${stamp}` : stamp
}

function sendDrawioMessage(message) {
  iframeRef.value?.contentWindow?.postMessage(JSON.stringify(message), drawioOrigin)
}

function sendSavedStatus(message = '已保存到账号') {
  if (!editorReady.value) return

  sendDrawioMessage({
    action: 'status',
    message,
    modified: false
  })
}

function loadXml(xml = savedXml.value) {
  if (!editorReady.value) return

  sendDrawioMessage({
    action: 'load',
    autosave: 1,
    title: 'xinming-drawio-demo.drawio',
    xml
  })
  drawioError.value = ''
}

function requestExport() {
  if (!editorReady.value) return

  sendDrawioMessage({ action: 'export', format: 'xml', spinKey: 'saving' })
  drawioError.value = ''
}

async function persistSyncedDiagram(xml = savedXml.value, { title = '', remark = '' } = {}) {
  const nextItemKey = createArchiveKey()
  const trimmedTitle = (title || '').trim()
  const trimmedRemark = (remark || '').trim()
  const item = await accountSync.saveItem({
    title: trimmedTitle || createArchiveTitle(),
    nextItemKey,
    payload: {
      xml,
      xml_length: xml.length,
      archive_key: nextItemKey,
      updated_from: 'diagrams.net',
      remark: trimmedRemark
    }
  })

  if (item) {
    drawioError.value = ''
    sendSavedStatus()
  }

  return item
}

async function saveSyncedDiagram() {
  if (!accountSync.auth.authenticated) {
    const authenticated = await accountSync.ensureAuth()
    if (!authenticated) {
      accountSync.login()
      return
    }
  }

  const active = accountSync.activeItem.value
  saveDialogDefaults.value = {
    title: active?.title || '',
    remark: active?.payload?.remark || ''
  }
  saveDialogOpen.value = true
}

async function handleSaveDialogConfirm({ title, remark }) {
  pendingArchiveMeta.value = { title, remark }
  saveDialogOpen.value = false

  if (editorReady.value) {
    syncAfterNextExport.value = true
    syncingExport.value = true
    requestExport()
    return
  }

  await persistSyncedDiagram(savedXml.value, { title, remark })
  pendingArchiveMeta.value = { title: '', remark: '' }
}

async function openArchive(item) {
  const xml = item?.payload?.xml
  if (typeof xml !== 'string' || !xml.trim()) {
    drawioError.value = '存档 XML 为空'
    return
  }

  accountSync.activeItem.value = item
  savedXml.value = xml
  savedAt.value = ''
  loadXml(xml)
  drawioError.value = ''
  historyOpen.value = false
}

async function deleteSyncedDiagram(item) {
  if (!item?.item_key) return

  deletingArchiveKey.value = item.item_key
  const deleted = await accountSync.deleteItem(item.item_key)
  if (deleted) {
    if (accountSync.activeItem.value?.item_key === item.item_key) {
      accountSync.activeItem.value = null
    }
    drawioError.value = ''
  }
  deletingArchiveKey.value = ''
}

function resetDemo() {
  savedXml.value = starterXml
  savedAt.value = ''
  iframeKey.value += 1
  editorReady.value = false
  syncAfterNextExport.value = false
  syncingExport.value = false
  drawioError.value = ''
}

function openStandalone() {
  window.open(drawioUrl, '_blank', 'noopener,noreferrer')
}

function parseDrawioMessage(data) {
  if (typeof data !== 'string') return null

  try {
    return JSON.parse(data)
  } catch {
    return null
  }
}

function handleDrawioMessage(event) {
  if (event.origin !== drawioOrigin) return

  const message = parseDrawioMessage(event.data)
  if (!message) return

  if (message.event === 'init') {
    editorReady.value = true
    loadXml()
    return
  }

  const xmlPayload = typeof message.xml === 'string' ? message.xml : message.data
  if ((message.event === 'save' || message.event === 'autosave' || message.event === 'export') && typeof xmlPayload === 'string') {
    savedXml.value = xmlPayload
    savedAt.value = new Intl.DateTimeFormat('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date())
    drawioError.value = ''
    if (syncAfterNextExport.value) {
      syncAfterNextExport.value = false
      syncingExport.value = false
      const meta = pendingArchiveMeta.value
      pendingArchiveMeta.value = { title: '', remark: '' }
      persistSyncedDiagram(xmlPayload, meta)
    } else if (message.event === 'save' && accountSync.auth.authenticated) {
      persistSyncedDiagram(xmlPayload)
    }
    return
  }

  if (message.error) {
    syncAfterNextExport.value = false
    syncingExport.value = false
    drawioError.value = `draw.io 返回错误：${message.error}`
    return
  }
}

onMounted(async () => {
  window.addEventListener('message', handleDrawioMessage)
  await accountSync.loadItems()
})

onUnmounted(() => {
  window.removeEventListener('message', handleDrawioMessage)
})
</script>

<template>
  <div class="tool-detail-page drawio-page">
    <ToolPageHeader
      title="Draw.io"
      kicker="Draw.io · iframe embed demo"
    />

    <section class="tool-detail-shell drawio-shell">
      <section class="drawio-canvas-workbench">
        <header class="drawio-workbench-toolbar">
          <section class="drawio-toolbar-block drawio-toolbar-save">
            <div class="drawio-toolbar-head">
              <div class="section-kicker">保存</div>
              <span
                v-if="syncStatusText"
                class="drawio-toolbar-status"
              >{{ syncStatusText }}</span>
            </div>

            <p class="drawio-editor-meta">{{ editorMetaText }}</p>

            <div
              v-if="drawioError || accountSync.errorMessage.value"
              class="drawio-notice drawio-notice-error"
            >
              {{ drawioError || accountSync.errorMessage.value }}
            </div>

            <div class="drawio-toolbar-actions">
              <button
                class="drawio-primary-action"
                type="button"
                :disabled="syncButtonDisabled"
                @click="saveSyncedDiagram"
              >
                {{ syncButtonText }}
              </button>
              <button
                class="drawio-ghost-action"
                type="button"
                :disabled="!editorReady"
                @click="requestExport"
              >
                导出 XML
              </button>
              <button
                class="drawio-ghost-action"
                type="button"
                :disabled="!editorReady"
                @click="loadXml()"
              >
                重新载入 XML
              </button>
              <button
                class="drawio-ghost-action"
                type="button"
                @click="resetDemo"
              >
                重置 Demo
              </button>

              <PopoverRoot v-model:open="historyOpen">
                <PopoverTrigger
                  class="drawio-ghost-action drawio-history-trigger"
                  :disabled="historyTriggerDisabled"
                  aria-label="历史存档"
                >
                  <span>{{ historyTriggerLabel }}</span>
                  <span
                    class="drawio-history-trigger-caret"
                    aria-hidden="true"
                  >▾</span>
                </PopoverTrigger>

                <PopoverPortal>
                  <PopoverContent
                    class="drawio-history-popover"
                    align="end"
                    :side-offset="8"
                  >
                    <div class="drawio-history-popover-head">
                      <div class="drawio-toolbar-head-left">
                        <div class="section-kicker">历史</div>
                        <span
                          v-if="archiveCountText"
                          class="drawio-archive-count"
                        >· {{ archiveCountText }}</span>
                      </div>
                      <button
                        class="drawio-ghost-action drawio-history-refresh"
                        type="button"
                        :disabled="accountSync.loading.value"
                        @click="accountSync.loadItems"
                      >
                        {{ accountSync.loading.value ? '刷新中' : '刷新' }}
                      </button>
                    </div>

                    <div
                      v-if="accountSync.loading.value && !accountSync.items.value.length"
                      class="drawio-history-popover-empty"
                    >
                      读取中
                    </div>
                    <div
                      v-else-if="!accountSync.items.value.length"
                      class="drawio-history-popover-empty"
                    >
                      无存档
                    </div>
                    <div
                      v-else
                      class="drawio-archive-list"
                    >
                      <div
                        v-for="item in accountSync.items.value"
                        :key="item.item_key"
                        class="drawio-archive-row"
                        :class="{ 'drawio-archive-row-active': accountSync.activeItem.value?.item_key === item.item_key }"
                      >
                        <button
                          class="drawio-archive-open"
                          type="button"
                          @click="openArchive(item)"
                        >
                          <span class="drawio-archive-title">{{ archiveDisplayTitle(item) }}</span>
                          <span class="drawio-archive-meta">{{ archiveSecondaryLine(item) }}</span>
                        </button>
                        <button
                          class="drawio-archive-delete"
                          type="button"
                          :disabled="deletingArchiveKey === item.item_key"
                          :aria-label="`删除 ${archiveDisplayTitle(item)}`"
                          @click.stop="deleteSyncedDiagram(item)"
                        >
                          {{ deletingArchiveKey === item.item_key ? '...' : '×' }}
                        </button>
                      </div>
                    </div>
                  </PopoverContent>
                </PopoverPortal>
              </PopoverRoot>
            </div>

            <AccountSyncPanel
              class="drawio-toolbar-sync"
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              @login="accountSync.login"
            />
          </section>
        </header>

        <section class="drawio-canvas-pane">
          <article class="drawio-panel drawio-editor-panel">
            <div class="drawio-editor-header">
              <button
                class="drawio-ghost-action"
                type="button"
                @click="openStandalone"
              >
                新窗口打开
              </button>
            </div>

            <iframe
              :key="iframeKey"
              ref="drawioFrame"
              class="drawio-frame"
              title="Draw.io embedded editor"
              :src="drawioUrl"
              allow="clipboard-read; clipboard-write"
            />
          </article>
        </section>
      </section>

      <ToolSaveDialog
        v-model:open="saveDialogOpen"
        :default-title="saveDialogDefaults.title"
        :default-remark="saveDialogDefaults.remark"
        :busy="accountSync.saving.value || syncingExport"
        dialog-title="保存到云端存档"
        @confirm="handleSaveDialogConfirm"
      />
    </section>
  </div>
</template>

<style scoped>
.drawio-shell {
  max-width: 1380px;
}

.drawio-panel {
  min-width: 0;
}

.drawio-canvas-workbench {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 28px;
}

.drawio-workbench-toolbar,
.drawio-canvas-pane {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
}

.drawio-workbench-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  padding: 18px;
}

.drawio-canvas-pane {
  padding: 22px;
}

.drawio-editor-header {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.drawio-toolbar-block {
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  min-width: 280px;
  padding: 14px;
}

.drawio-toolbar-save {
  flex: 1 1 100%;
}

.drawio-history-trigger {
  display: inline-flex;
  max-width: 320px;
}

.drawio-history-trigger > span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drawio-history-trigger-caret {
  font-size: 0.78rem;
  margin-left: 2px;
}

.drawio-history-refresh {
  min-height: 32px;
  padding: 0 10px;
  font-size: 0.82rem;
}

.drawio-toolbar-head,
.drawio-toolbar-actions {
  display: flex;
  gap: 10px;
}

.drawio-toolbar-head {
  align-items: center;
  justify-content: space-between;
}

.drawio-toolbar-head-left {
  align-items: baseline;
  display: flex;
  gap: 6px;
}

.drawio-archive-count {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
}

.drawio-toolbar-status {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.drawio-editor-meta {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
  margin: 12px 0 0;
}

.drawio-toolbar-actions {
  flex-wrap: wrap;
  margin-top: 12px;
}

.drawio-toolbar-sync {
  margin-top: 12px;
}

.drawio-notice {
  background: rgba(16, 37, 66, 0.06);
  border: 1px solid rgba(16, 37, 66, 0.08);
  border-radius: 16px;
  color: rgba(15, 23, 35, 0.72);
  line-height: 1.6;
  margin-top: 16px;
  padding: 14px 16px;
}

.drawio-notice-error {
  background: rgba(193, 0, 21, 0.08);
  border-color: rgba(193, 0, 21, 0.16);
  color: #8d1120;
}

.drawio-primary-action,
.drawio-ghost-action {
  align-items: center;
  border-radius: var(--brand-radius-pill, 999px);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
}

.drawio-primary-action {
  background: var(--brand-color-accent, #102542);
  border: 1px solid var(--brand-color-accent, #102542);
  color: #ffffff;
}

.drawio-ghost-action {
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  color: var(--shell-navy);
}

.drawio-ghost-action:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.drawio-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.drawio-primary-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.drawio-primary-action:focus-visible,
.drawio-ghost-action:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.drawio-frame {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  height: min(72vh, 760px);
  margin-top: 16px;
  min-height: 620px;
  width: 100%;
}

@media (max-width: 1023px) {
  .drawio-frame {
    height: 580px;
  }
}

@media (max-width: 599px) {
  .drawio-editor-header,
  .drawio-toolbar-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .drawio-frame {
    height: 520px;
    min-height: 520px;
  }

  .drawio-toolbar-block {
    min-width: 0;
    width: 100%;
  }

  .drawio-workbench-toolbar,
  .drawio-canvas-pane {
    padding: 18px;
  }
}
</style>

<style>
/* Unscoped: PopoverPortal teleports PopoverContent to <body>, so scoped
   selectors with data-v-XXX attributes do not reliably reach the
   portal-mounted subtree. These classes are namespaced enough not to leak. */
.drawio-history-popover {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  color: var(--shell-navy, #102542);
  min-width: 320px;
  padding: 12px;
  z-index: 90;
}

.drawio-history-popover:focus-visible {
  outline: none;
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.drawio-history-popover-head {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.drawio-history-popover-empty {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
  margin-top: 10px;
  padding: 6px 4px;
}

.drawio-archive-list {
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

.drawio-archive-list::-webkit-scrollbar {
  width: 8px;
}

.drawio-archive-list::-webkit-scrollbar-thumb {
  background: rgba(16, 37, 66, 0.2);
  border-radius: 999px;
}

.drawio-archive-row {
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

.drawio-archive-row:first-child {
  border-top: 0;
}

.drawio-archive-row:hover,
.drawio-archive-row:focus-within {
  background: rgba(16, 37, 66, 0.04);
}

.drawio-archive-row-active {
  background: rgba(16, 37, 66, 0.06);
  box-shadow: inset 3px 0 0 0 var(--brand-color-accent, #102542);
}

.drawio-archive-open {
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

.drawio-archive-open:focus-visible {
  border-radius: var(--brand-radius-sm, 8px);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.drawio-archive-title {
  color: var(--shell-navy, #102542);
  font-size: 0.88rem;
  font-weight: 700;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drawio-archive-meta {
  color: rgba(15, 23, 35, 0.55);
  font-size: 0.8rem;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.drawio-archive-delete {
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

.drawio-archive-row:hover .drawio-archive-delete,
.drawio-archive-row:focus-within .drawio-archive-delete {
  color: var(--shell-coral, #ff7a59);
}

.drawio-archive-delete:hover {
  background: rgba(255, 122, 89, 0.12);
  color: var(--shell-coral, #ff7a59);
}

.drawio-archive-delete:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  color: var(--shell-coral, #ff7a59);
  outline: none;
}

.drawio-archive-delete:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
