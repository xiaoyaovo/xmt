<script setup>
import { computed, onMounted, onUnmounted, shallowRef, useTemplateRef } from 'vue'

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
const lastEvent = shallowRef('等待编辑器初始化')
const savedAt = shallowRef('')
const messageCount = shallowRef(0)
const iframeKey = shallowRef(0)

const xmlCharacters = computed(() => savedXml.value.length)
const savedAtText = computed(() => savedAt.value || '尚未保存')
const editorStatus = computed(() => (editorReady.value ? '已连接' : '初始化中'))
const stats = computed(() => [
  { label: '连接', value: editorStatus.value },
  { label: '消息', value: messageCount.value },
  { label: 'XML', value: xmlCharacters.value },
  { label: '保存', value: savedAtText.value }
])

function sendDrawioMessage(message) {
  iframeRef.value?.contentWindow?.postMessage(JSON.stringify(message), drawioOrigin)
}

function loadXml(xml = savedXml.value) {
  if (!editorReady.value) {
    lastEvent.value = '编辑器尚未初始化，稍后会自动载入。'
    return
  }

  sendDrawioMessage({
    action: 'load',
    autosave: 1,
    title: 'xinming-drawio-demo.drawio',
    xml
  })
  lastEvent.value = '已把当前 XML 载入 draw.io。'
}

function requestExport() {
  if (!editorReady.value) {
    lastEvent.value = '编辑器尚未初始化，暂时不能导出 XML。'
    return
  }

  sendDrawioMessage({ action: 'export', format: 'xml', spinKey: 'saving' })
  lastEvent.value = '已向 draw.io 请求导出 XML。'
}

function resetDemo() {
  savedXml.value = starterXml
  savedAt.value = ''
  iframeKey.value += 1
  editorReady.value = false
  lastEvent.value = '已恢复示例图，正在重新载入编辑器。'
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

  messageCount.value += 1

  if (message.event === 'init') {
    editorReady.value = true
    lastEvent.value = 'draw.io 已初始化。'
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
    lastEvent.value = message.event === 'autosave' ? '已收到自动保存 XML。' : '已收到 draw.io XML。'
    return
  }

  if (message.event === 'exit') {
    lastEvent.value = 'draw.io 发送了退出事件，demo 会保留当前页面。'
    return
  }

  lastEvent.value = `收到 draw.io 事件：${message.event || 'unknown'}`
}

onMounted(() => {
  window.addEventListener('message', handleDrawioMessage)
})

onUnmounted(() => {
  window.removeEventListener('message', handleDrawioMessage)
})
</script>

<template>
  <div class="tool-detail-page drawio-page">
    <section class="tool-detail-shell drawio-shell">
      <div class="tool-detail-header">
        <div>
          <div class="section-kicker">Draw.io · iframe embed demo</div>
          <h1 class="section-title">把完整画图编辑器嵌进工具台。</h1>
        </div>
        <p class="section-text">
          这个 demo 使用官方 diagrams.net embed 页面运行 draw.io，当前页面负责载入 XML、接收保存结果和展示通信状态。
        </p>
      </div>

      <section class="drawio-workspace">
        <aside class="drawio-sidebar">
          <article class="drawio-panel">
            <div class="drawio-panel-topline">
              <div>
                <div class="section-kicker">通信</div>
                <h2 class="bench-title">宿主页状态</h2>
              </div>
              <span class="drawio-status">{{ editorStatus }}</span>
            </div>

            <div class="drawio-summary-grid">
              <div
                v-for="item in stats"
                :key="item.label"
                class="drawio-summary-card"
              >
                <div class="drawio-summary-value">{{ item.value }}</div>
                <div class="drawio-summary-label">{{ item.label }}</div>
              </div>
            </div>

            <div class="drawio-notice">
              {{ lastEvent }}
            </div>

            <div class="drawio-actions">
              <button
                class="drawio-primary-action"
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
            </div>
          </article>

          <article class="drawio-panel">
            <div class="section-kicker">数据</div>
            <h2 class="bench-title">最近保存的 XML</h2>
            <p class="drawio-helper">
              当前只保存在浏览器内存里。正式接入时，可以把这段 XML 写入账号同步或图表历史。
            </p>
            <textarea
              class="drawio-xml-preview"
              :value="savedXml"
              readonly
              aria-label="最近保存的 draw.io XML"
            />
          </article>
        </aside>

        <main class="drawio-main">
          <article class="drawio-panel drawio-editor-panel">
            <div class="drawio-editor-header">
              <div>
                <div class="section-kicker">编辑器</div>
                <h2 class="drawio-file-title">diagrams.net embed</h2>
              </div>
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
        </main>
      </section>
    </section>
  </div>
</template>

<style scoped>
.drawio-shell {
  max-width: 1380px;
}

.drawio-workspace {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(320px, 0.34fr) minmax(0, 0.66fr);
  margin-top: 28px;
}

.drawio-sidebar,
.drawio-main {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.drawio-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
  padding: 22px;
}

.drawio-panel-topline,
.drawio-editor-header {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.drawio-status,
.drawio-helper {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.drawio-summary-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 16px;
}

.drawio-summary-card {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line);
  border-radius: 18px;
  min-width: 0;
  padding: 14px;
}

.drawio-summary-value {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.1rem, 2vw, 1.55rem);
  font-weight: 700;
  overflow-wrap: anywhere;
}

.drawio-summary-label {
  color: rgba(15, 23, 35, 0.6);
  font-size: 0.84rem;
  margin-top: 6px;
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

.drawio-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
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
  border: 0;
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

.drawio-primary-action:disabled,
.drawio-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.drawio-helper {
  line-height: 1.6;
  margin: 12px 0 0;
}

.drawio-xml-preview {
  background: #0f1723;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  color: #edf6ff;
  font: 0.82rem/1.55 "SFMono-Regular", "Cascadia Code", "Liberation Mono", monospace;
  margin-top: 14px;
  min-height: 220px;
  outline: none;
  padding: 14px;
  resize: vertical;
  width: 100%;
}

.drawio-editor-panel {
  min-height: 760px;
}

.drawio-file-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.4rem, 2.5vw, 2rem);
  font-weight: 800;
  margin: 8px 0 0;
}

.drawio-frame {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  height: 680px;
  margin-top: 16px;
  width: 100%;
}

@media (max-width: 1023px) {
  .drawio-workspace {
    grid-template-columns: 1fr;
  }

  .drawio-editor-panel {
    min-height: 660px;
  }

  .drawio-frame {
    height: 580px;
  }
}

@media (max-width: 599px) {
  .drawio-panel {
    padding: 18px;
  }

  .drawio-panel-topline,
  .drawio-editor-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .drawio-summary-grid {
    grid-template-columns: 1fr;
  }

  .drawio-frame {
    height: 520px;
  }
}
</style>
