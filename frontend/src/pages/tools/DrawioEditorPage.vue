<script setup>
import { computed, onMounted, onUnmounted, shallowRef, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'

import ToolVersionMenu from 'src/components/tools/ToolVersionMenu.vue'
import { useToolVersions } from 'src/composables/useToolVersions'

const drawioOrigin = 'https://drawio.cxmjtt.com'
const drawioPath = '/drawio/'
const drawioStandaloneUrl = `${drawioOrigin}${drawioPath}?ui=min&lang=zh&dark=0&libraries=1`
const editorRevealDelay = 900
const editorRevealFallbackDelay = 7000
const route = useRoute()
const diagramStarterXml = `<mxfile host="xinming-tools" modified="2026-05-25T00:00:00.000Z" agent="Xinming Tools" version="30.0.2">
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
const whiteboardStarterXml = `<mxfile host="xinming-tools" modified="2026-05-25T00:00:00.000Z" agent="Xinming Tools" version="30.0.2">
  <diagram id="xinming-whiteboard" name="Whiteboard">
    <mxGraphModel dx="1120" dy="680" grid="0" gridSize="10" guides="0" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="1100" pageHeight="850" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`

function resolveEditorMode() {
  return route.query.mode === 'whiteboard' ? 'whiteboard' : 'diagram'
}

function resolveStarterXml(mode = resolveEditorMode()) {
  return mode === 'whiteboard' ? whiteboardStarterXml : diagramStarterXml
}

const iframeRef = useTemplateRef('drawioFrame')
const savedXml = shallowRef(resolveStarterXml())
const editorReady = shallowRef(false)
const editorVisible = shallowRef(false)
const drawioError = shallowRef('')
const savedAt = shallowRef('')
const iframeKey = shallowRef(0)
const syncAfterNextExport = shallowRef(false)
const syncingExport = shallowRef(false)
const pendingArchiveMeta = shallowRef({ forceNew: false, title: '', remark: '' })
let editorRevealTimer = null

const editorMode = computed(() => resolveEditorMode())
const editorModeLabel = computed(() => editorMode.value === 'whiteboard' ? '白板' : 'Draw.io')

async function exportThenPersist({ forceNew, title, remark, persist }) {
  if (!editorReady.value) {
    return persist({ forceNew, title, remark })
  }
  pendingArchiveMeta.value = { forceNew, title, remark }
  syncAfterNextExport.value = true
  syncingExport.value = true
  requestExport()
  return null
}

function makeDrawioVersions(toolKey) {
  return useToolVersions(toolKey, {
    defaultTitlePrefix: 'Draw.io 图表',
    updatedFrom: 'diagrams.net',
    buildPayload: ({ archiveKey, remark, updatedFrom }) => ({
      xml: savedXml.value,
      xml_length: savedXml.value.length,
      archive_key: archiveKey,
      mode: editorMode.value,
      updated_from: updatedFrom,
      remark
    }),
    applyPayload: payload => {
      if (typeof payload?.xml !== 'string' || !payload.xml.trim()) {
        drawioError.value = '存档 XML 为空'
        return false
      }
      savedXml.value = payload.xml
      savedAt.value = ''
      loadXml(payload.xml)
      drawioError.value = ''
      return true
    },
    saveStrategy: exportThenPersist
  })
}

const diagramVersions = makeDrawioVersions('drawio')
const whiteboardVersions = makeDrawioVersions('drawio-whiteboard')
const versions = computed(() => editorMode.value === 'whiteboard' ? whiteboardVersions : diagramVersions)

const starterXml = computed(() => resolveStarterXml(editorMode.value))
const drawioEmbedUrl = computed(() => {
  const modeParams = editorMode.value === 'whiteboard' ? 'ui=min&sketch=1' : 'ui=min'
  return `${drawioOrigin}${drawioPath}?embed=1&proto=json&spin=1&${modeParams}&lang=zh&dark=0&libraries=1&saveAndExit=0&noSaveBtn=0&noExitBtn=1`
})
const xmlCharacters = computed(() => savedXml.value.length)
const editorMetaText = computed(() => {
  const parts = [`${xmlCharacters.value} 字符`]
  if (savedAt.value) parts.push(`已保存 ${savedAt.value}`)
  return parts.join(' · ')
})
const syncStatusText = computed(() => {
  if (syncingExport.value) return '准备同步'
  return versions.value.syncStatusText.value
})

function sendDrawioMessage(message) {
  iframeRef.value?.contentWindow?.postMessage(JSON.stringify(message), drawioOrigin)
}

function clearEditorRevealTimer() {
  if (editorRevealTimer === null) return

  window.clearTimeout(editorRevealTimer)
  editorRevealTimer = null
}

function hideEditorUntilLoaded() {
  clearEditorRevealTimer()
  editorVisible.value = false
}

function scheduleEditorReveal() {
  clearEditorRevealTimer()
  editorRevealTimer = window.setTimeout(() => {
    editorVisible.value = true
    editorRevealTimer = null
  }, editorRevealDelay)
}

function scheduleEditorFallbackReveal() {
  if (editorVisible.value || editorRevealTimer !== null) return

  editorRevealTimer = window.setTimeout(() => {
    editorVisible.value = true
    editorRevealTimer = null
  }, editorRevealFallbackDelay)
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

  hideEditorUntilLoaded()
  sendDrawioMessage({
    action: 'load',
    autosave: 1,
    title: `xinming-${editorMode.value}.drawio`,
    xml,
    ...(editorMode.value === 'whiteboard' ? { rough: 1, toSketch: 1 } : {})
  })
  drawioError.value = ''
  scheduleEditorReveal()
}

function requestExport() {
  if (!editorReady.value) return

  sendDrawioMessage({ action: 'export', format: 'xml', spinKey: 'saving' })
  drawioError.value = ''
}

function handleIframeLoad() {
  scheduleEditorFallbackReveal()
}

function resetDemo() {
  hideEditorUntilLoaded()
  scheduleEditorFallbackReveal()
  savedXml.value = starterXml.value
  savedAt.value = ''
  iframeKey.value += 1
  editorReady.value = false
  syncAfterNextExport.value = false
  syncingExport.value = false
  drawioError.value = ''
}

function openStandalone() {
  window.open(drawioStandaloneUrl, '_blank', 'noopener,noreferrer')
}

function parseDrawioMessage(data) {
  if (typeof data !== 'string') return null

  try {
    return JSON.parse(data)
  } catch {
    return null
  }
}

async function persistFromExport() {
  syncAfterNextExport.value = false
  syncingExport.value = false
  const meta = pendingArchiveMeta.value
  pendingArchiveMeta.value = { forceNew: false, title: '', remark: '' }
  const item = await versions.value.persist({
    forceNew: meta.forceNew,
    title: meta.title,
    remark: meta.remark
  })
  if (item) {
    drawioError.value = ''
    sendSavedStatus()
  }
}

async function persistAutoSave() {
  if (!versions.value.auth.authenticated) return
  const item = await versions.value.persist({})
  if (item) {
    drawioError.value = ''
    sendSavedStatus()
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
      persistFromExport()
    } else if (message.event === 'save') {
      persistAutoSave()
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
  scheduleEditorFallbackReveal()
  await versions.value.loadInitial()
})

onUnmounted(() => {
  clearEditorRevealTimer()
  window.removeEventListener('message', handleDrawioMessage)
})

watch(editorMode, async () => {
  hideEditorUntilLoaded()
  scheduleEditorFallbackReveal()
  savedXml.value = starterXml.value
  savedAt.value = ''
  iframeKey.value += 1
  editorReady.value = false
  syncAfterNextExport.value = false
  syncingExport.value = false
  drawioError.value = ''
  await versions.value.loadInitial()
})
</script>

<template>
  <div class="drawio-editor-page">
    <header class="drawio-editor-toolbar">
      <div class="drawio-editor-title-block">
        <UButton
          class="drawio-back-link"
          color="neutral"
          label="← 工具"
          to="/tools"
          variant="subtle"
        />
        <div class="drawio-title-copy">
          <span class="drawio-kicker">Xinming · 全屏编辑</span>
          <h1 class="drawio-title">{{ editorModeLabel }}</h1>
        </div>
      </div>

      <div class="drawio-toolbar-main">
        <ToolVersionMenu
          :versions="versions"
          :save-disabled="syncingExport"
        />

        <UButton
          class="drawio-ghost-action"
          color="neutral"
          label="导出 XML"
          type="button"
          variant="subtle"
          :disabled="!editorReady"
          @click="requestExport"
        />
        <UButton
          class="drawio-ghost-action"
          color="neutral"
          label="重新载入"
          type="button"
          variant="subtle"
          :disabled="!editorReady"
          @click="loadXml()"
        />
        <UButton
          class="drawio-ghost-action"
          color="neutral"
          label="重置"
          type="button"
          variant="subtle"
          @click="resetDemo"
        />
        <UButton
          class="drawio-ghost-action"
          color="neutral"
          label="原始编辑器"
          type="button"
          variant="subtle"
          @click="openStandalone"
        />
      </div>

      <div class="drawio-toolbar-meta">
        <span>{{ editorMetaText }}</span>
        <span v-if="syncStatusText">{{ syncStatusText }}</span>
        <span
          v-if="drawioError || versions.errorMessage.value"
          class="drawio-inline-error"
        >
          {{ drawioError || versions.errorMessage.value }}
        </span>
      </div>

    </header>

    <main class="drawio-editor-main">
      <iframe
        :key="iframeKey"
        ref="drawioFrame"
        class="drawio-frame"
        :class="{ 'drawio-frame-visible': editorVisible }"
        title="Draw.io embedded editor"
        :src="drawioEmbedUrl"
        allow="clipboard-read; clipboard-write"
        @load="handleIframeLoad"
      />
      <div
        v-if="!editorVisible"
        class="drawio-loading-cover"
        role="status"
        aria-live="polite"
      >
        <div class="drawio-loading-copy">
          <span class="drawio-loading-kicker">Xinming</span>
          <span class="drawio-loading-title">正在准备{{ editorModeLabel }}</span>
          <span class="drawio-loading-text">加载画布中</span>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.drawio-editor-page {
  background: #f6f8fb;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100dvh;
  min-height: 100dvh;
  overflow: hidden;
  padding-bottom: env(safe-area-inset-bottom, 0);
}

.drawio-editor-toolbar {
  align-items: center;
  background: rgba(247, 250, 253, 0.96);
  border-bottom: 1px solid rgba(16, 37, 66, 0.1);
  display: grid;
  gap: 10px 16px;
  grid-template-columns: minmax(190px, auto) minmax(0, 1fr);
  padding: calc(10px + env(safe-area-inset-top, 0)) 14px 10px;
  z-index: 5;
}

.drawio-editor-title-block {
  align-items: center;
  display: flex;
  gap: 12px;
  min-width: 0;
}

.drawio-back-link {
  align-items: center;
  background: #ffffff;
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-navy);
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 0.84rem;
  font-weight: 800;
  min-height: 34px;
  padding: 0 12px;
  text-decoration: none;
}

.drawio-title-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.drawio-kicker,
.drawio-toolbar-meta {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.74rem;
  font-weight: 700;
}

.drawio-kicker {
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.drawio-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.12rem;
  line-height: 1.1;
  margin: 0;
}

.drawio-toolbar-main {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
  min-width: 0;
}

.drawio-toolbar-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  grid-column: 2;
  justify-content: flex-end;
  min-width: 0;
}

.drawio-inline-error {
  color: #8d1120;
}

.drawio-ghost-action {
  align-items: center;
  border-radius: var(--brand-radius-md, 16px);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
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

.drawio-ghost-action:focus-visible,
.drawio-back-link:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.drawio-editor-main {
  background: #ffffff;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.drawio-frame {
  background: #ffffff;
  border: 0;
  display: block;
  height: 100%;
  opacity: 0;
  transition: opacity 180ms ease;
  width: 100%;
}

.drawio-frame-visible {
  opacity: 1;
}

.drawio-loading-cover {
  align-items: center;
  background:
    linear-gradient(90deg, rgba(16, 37, 66, 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgba(16, 37, 66, 0.035) 1px, transparent 1px),
    #f8fafc;
  background-size: 36px 36px;
  color: var(--shell-navy);
  display: flex;
  inset: 0;
  justify-content: center;
  padding: 24px;
  position: absolute;
  z-index: 2;
}

.drawio-loading-copy {
  align-items: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: center;
}

.drawio-loading-kicker {
  color: rgba(15, 23, 35, 0.52);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.drawio-loading-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.35rem;
  line-height: 1.2;
}

.drawio-loading-text {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.88rem;
  font-weight: 700;
}

@media (prefers-reduced-motion: reduce) {
  .drawio-frame {
    transition: none;
  }
}

@media (max-width: 920px) {
  .drawio-editor-toolbar {
    align-items: stretch;
    grid-template-columns: 1fr;
  }

  .drawio-toolbar-main,
  .drawio-toolbar-meta {
    grid-column: 1;
    justify-content: flex-start;
  }

}

@media (max-width: 599px) {
  .drawio-editor-toolbar {
    gap: 8px;
    padding: calc(8px + env(safe-area-inset-top, 0)) 10px 8px;
  }

  .drawio-editor-title-block {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }

  .drawio-ghost-action {
    min-height: 34px;
    padding: 0 10px;
  }

  .drawio-title {
    font-size: 1rem;
  }
}
</style>
