<script setup>
import { computed, onMounted, shallowRef } from 'vue'
import xmlFormat from 'xml-formatter'

import MonacoEditor from 'src/components/editors/MonacoEditor.vue'
import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import ToolVersionMenu from 'src/components/tools/ToolVersionMenu.vue'
import ToolWorkbench from 'src/components/tools/ToolWorkbench.vue'
import { useToolVersions } from 'src/composables/useToolVersions'

const defaultSource = `<?xml version="1.0" encoding="UTF-8"?>
<catalog>
  <book id="b001" category="tech">
    <title lang="zh">深入理解 XML</title>
    <author>张三</author>
    <year>2024</year>
    <price currency="CNY">59.00</price>
  </book>
  <book id="b002" category="novel">
    <title lang="en">The Quiet Sea</title>
    <author>Jane Doe</author>
    <year>2023</year>
    <price currency="USD">12.50</price>
  </book>
</catalog>`

const indentOptions = [
  { label: '2 空格', value: '2' },
  { label: '4 空格', value: '4' },
  { label: 'Tab', value: 'tab' }
]

const source = shallowRef(defaultSource)
const output = shallowRef('')
const indentChoice = shallowRef('2')
const errorMessage = shallowRef('')
const errorLine = shallowRef(0)
const errorColumn = shallowRef(0)
const valid = shallowRef(null)
const copied = shallowRef(false)
const lastAction = shallowRef('')

const trimmedSource = computed(() => source.value.trim())

const indentString = computed(() => {
  if (indentChoice.value === 'tab') return '\t'
  const width = Number(indentChoice.value) || 2
  return ' '.repeat(width)
})

const sourceLines = computed(() => source.value.split('\n').length)
const sourceChars = computed(() => source.value.length)
const outputBytes = computed(() => new Blob([output.value]).size)

const statusText = computed(() => {
  if (valid.value === null) return '等待校验'
  return valid.value ? '格式有效' : '格式异常'
})

const statusTone = computed(() => {
  if (valid.value === null) return 'pending'
  return valid.value ? 'ok' : 'error'
})

const versions = useToolVersions('xml', {
  defaultTitlePrefix: 'XML 文档',
  updatedFrom: 'xml-editor',
  buildPayload: ({ archiveKey, remark, updatedFrom }) => ({
    source: source.value,
    line_count: sourceLines.value,
    character_count: sourceChars.value,
    indent_choice: indentChoice.value,
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
    if (payload.indent_choice) indentChoice.value = String(payload.indent_choice)
    output.value = ''
    valid.value = null
    clearError()
    copied.value = false
    lastAction.value = ''
    return true
  }
})

function parseXmlDocument(text) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(text, 'application/xml')
  const errorNode = doc.getElementsByTagName('parsererror')[0]
  if (errorNode) {
    return { ok: false, doc: null, error: errorNode.textContent || '解析失败' }
  }
  return { ok: true, doc, error: '' }
}

function extractErrorPosition(message) {
  if (!message) return { line: 0, column: 0 }
  const lineMatch = message.match(/line(?:\s*number)?[^\d]*(\d+)/i)
  const columnMatch = message.match(/column(?:\s*number)?[^\d]*(\d+)/i)
  return {
    line: lineMatch ? Number(lineMatch[1]) : 0,
    column: columnMatch ? Number(columnMatch[1]) : 0
  }
}

function setError(message) {
  errorMessage.value = message
  const { line, column } = extractErrorPosition(message)
  errorLine.value = line
  errorColumn.value = column
  valid.value = false
}

function clearError() {
  errorMessage.value = ''
  errorLine.value = 0
  errorColumn.value = 0
}

function formatXmlSource(text, indent) {
  return xmlFormat(text, {
    indentation: indent,
    collapseContent: true,
    lineSeparator: '\n',
    throwOnFailure: true,
    strictMode: true
  })
}

function minifyXmlSource(text) {
  return xmlFormat.minify(text, {
    collapseContent: true,
    throwOnFailure: true,
    strictMode: true
  })
}

function runValidate() {
  copied.value = false
  lastAction.value = 'validate'
  if (!trimmedSource.value) {
    valid.value = null
    clearError()
    output.value = ''
    return
  }
  const result = parseXmlDocument(source.value)
  if (!result.ok) {
    setError(result.error)
    output.value = ''
    return
  }
  valid.value = true
  clearError()
  output.value = source.value
}

function runFormat() {
  copied.value = false
  lastAction.value = 'format'
  if (!trimmedSource.value) {
    valid.value = null
    clearError()
    output.value = ''
    return
  }
  const result = parseXmlDocument(source.value)
  if (!result.ok) {
    setError(result.error)
    output.value = ''
    return
  }
  valid.value = true
  clearError()
  try {
    output.value = formatXmlSource(source.value, indentString.value)
  } catch (error) {
    setError(error?.message || '格式化失败')
    output.value = ''
  }
}

function runMinify() {
  copied.value = false
  lastAction.value = 'minify'
  if (!trimmedSource.value) {
    valid.value = null
    clearError()
    output.value = ''
    return
  }
  const result = parseXmlDocument(source.value)
  if (!result.ok) {
    setError(result.error)
    output.value = ''
    return
  }
  valid.value = true
  clearError()
  try {
    output.value = minifyXmlSource(source.value)
  } catch (error) {
    setError(error?.message || '压缩失败')
    output.value = ''
  }
}

function loadSample() {
  source.value = defaultSource
  output.value = ''
  valid.value = null
  clearError()
  copied.value = false
  lastAction.value = ''
}

function clearAll() {
  source.value = ''
  output.value = ''
  valid.value = null
  clearError()
  copied.value = false
  lastAction.value = ''
}

function applyToSource() {
  if (!output.value) return
  source.value = output.value
  copied.value = false
}

async function copyOutput() {
  if (!output.value) return
  try {
    await navigator.clipboard.writeText(output.value)
    copied.value = true
    window.setTimeout(() => {
      copied.value = false
    }, 1600)
  } catch {
    copied.value = false
  }
}

function downloadOutput() {
  if (!output.value) return
  const blob = new Blob([output.value], { type: 'application/xml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `xml-${lastAction.value || 'result'}-${Date.now()}.xml`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function updateSource(value) {
  source.value = value ?? ''
  if (valid.value !== null) {
    valid.value = null
    clearError()
  }
}

async function onDropFile(event) {
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  if (!/xml|text/.test(file.type) && !/\.xml$/i.test(file.name)) {
    setError('仅支持 .xml 文本文件')
    return
  }
  const text = await file.text()
  updateSource(text)
}

onMounted(() => versions.loadInitial())
</script>

<template>
  <div class="tool-detail-page xml-tool-page">
    <ToolPageHeader
      title="XML"
      kicker="XML · 校验与格式化"
    />

    <section class="tool-detail-shell">
      <ToolWorkbench>
        <template #toolbar>
          <section class="xml-toolbar-block">
            <div class="xml-toolbar-head">
              <div class="section-kicker">操作</div>
              <span
                class="xml-status"
                :data-tone="statusTone"
              >{{ statusText }}</span>
              <span
                v-if="versions.syncStatusText.value"
                class="xml-status xml-status-sync"
              >{{ versions.syncStatusText.value }}</span>
            </div>

            <div class="xml-toolbar-actions">
              <UButton
                class="xml-primary-action brand-action-button"
                color="primary"
                label="校验"
                type="button"
                :disabled="!trimmedSource"
                @click="runValidate"
              />
              <UButton
                class="xml-primary-action brand-action-button"
                color="primary"
                label="格式化"
                type="button"
                :disabled="!trimmedSource"
                @click="runFormat"
              />
              <UButton
                class="xml-ghost-action"
                color="neutral"
                label="压缩"
                type="button"
                variant="subtle"
                :disabled="!trimmedSource"
                @click="runMinify"
              />

              <USelect
                class="xml-indent-select"
                :items="indentOptions"
                :model-value="indentChoice"
                aria-label="缩进设置"
                @update:model-value="value => (indentChoice = value)"
              />

              <ToolVersionMenu
                :versions="versions"
                :save-disabled="!trimmedSource"
                save-dialog-title="保存到云端存档"
                save-as-dialog-title="另存为新版本"
              />

              <UButton
                class="xml-ghost-action"
                color="neutral"
                label="示例"
                type="button"
                variant="subtle"
                @click="loadSample"
              />
              <UButton
                class="xml-ghost-action"
                color="neutral"
                label="清空"
                type="button"
                variant="subtle"
                :disabled="!source && !output"
                @click="clearAll"
              />
            </div>

            <p class="xml-toolbar-hint">
              {{ sourceLines }} 行 · {{ sourceChars }} 字符
              <span v-if="output"> · 结果 {{ outputBytes }} B</span>
            </p>

            <div
              v-if="versions.errorMessage.value"
              class="xml-notice xml-notice-error xml-notice-sync"
            >
              <div class="xml-notice-title">同步错误</div>
              <pre class="xml-notice-detail">{{ versions.errorMessage.value }}</pre>
            </div>
          </section>
        </template>

        <template #source>
          <article class="xml-panel xml-edit-panel">
            <div
              v-if="errorMessage"
              class="xml-notice xml-notice-error"
            >
              <div class="xml-notice-title">
                解析错误<span
                  v-if="errorLine"
                  class="xml-notice-pos"
                > · 第 {{ errorLine }} 行<span v-if="errorColumn">，第 {{ errorColumn }} 列</span></span>
              </div>
              <pre class="xml-notice-detail">{{ errorMessage }}</pre>
            </div>

            <div
              class="xml-editor-shell"
              @dragover.prevent
              @drop.prevent="onDropFile"
            >
              <MonacoEditor
                v-model="source"
                language="xml"
                aria-label="XML 源码编辑器"
                :min-height="560"
                :options="{ wordWrap: 'on', tabSize: 2 }"
              />
            </div>
          </article>
        </template>

        <template #preview>
          <article class="xml-panel xml-preview-panel">
            <div class="xml-preview-head">
              <div class="xml-preview-meta">
                <span class="xml-preview-label">结果</span>
                <span
                  v-if="lastAction"
                  class="xml-preview-action"
                >{{
                  lastAction === 'validate' ? '已校验'
                  : lastAction === 'format' ? '已格式化'
                  : lastAction === 'minify' ? '已压缩'
                  : ''
                }}</span>
              </div>
              <div class="xml-preview-actions">
                <UButton
                  class="xml-ghost-action"
                  color="neutral"
                  :label="copied ? '已复制' : '复制'"
                  type="button"
                  variant="subtle"
                  :disabled="!output"
                  @click="copyOutput"
                />
                <UButton
                  class="xml-ghost-action"
                  color="neutral"
                  label="下载"
                  type="button"
                  variant="subtle"
                  :disabled="!output"
                  @click="downloadOutput"
                />
                <UButton
                  class="xml-ghost-action"
                  color="neutral"
                  label="回填到源码"
                  type="button"
                  variant="subtle"
                  :disabled="!output"
                  @click="applyToSource"
                />
              </div>
            </div>

            <MonacoEditor
              v-if="output"
              :model-value="output"
              language="xml"
              read-only
              aria-label="XML 结果"
              :min-height="520"
              :options="{ wordWrap: 'on' }"
            />
            <div
              v-else
              class="xml-output-empty"
            >
              点击「校验」「格式化」或「压缩」查看结果。
            </div>
          </article>
        </template>
      </ToolWorkbench>
    </section>
  </div>
</template>

<style scoped>
.xml-panel {
  min-width: 0;
}

.xml-edit-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.xml-toolbar-block {
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  flex: 1 1 100%;
  min-width: 280px;
  padding: 14px;
}

.xml-toolbar-head {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.xml-toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.xml-toolbar-hint {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
  margin: 12px 0 0;
}

.xml-status {
  font-size: 0.85rem;
  font-weight: 700;
}

.xml-status[data-tone='pending'] {
  color: rgba(15, 23, 35, 0.62);
}

.xml-status[data-tone='ok'] {
  color: #1f7a3a;
}

.xml-status[data-tone='error'] {
  color: #9b2f25;
}

.xml-status-sync {
  color: rgba(15, 23, 35, 0.62);
  font-weight: 600;
}

.xml-primary-action,
.xml-ghost-action {
  align-items: center;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--shell-navy);
  cursor: pointer;
  display: inline-flex;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 800;
  gap: 8px;
  min-height: 38px;
  padding: 0 13px;
}

.xml-primary-action {
  background: var(--brand-color-accent, #102542);
  border-color: var(--brand-color-accent, #102542);
  color: #ffffff;
}

.xml-primary-action:disabled,
.xml-ghost-action:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.xml-ghost-action:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.xml-primary-action:focus-visible,
.xml-ghost-action:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.xml-indent-select {
  min-width: 112px;
}

.xml-notice {
  border: 1px solid rgba(155, 47, 37, 0.24);
  border-radius: var(--brand-radius-md, 16px);
  padding: 10px 12px;
}

.xml-notice-error {
  background: rgba(155, 47, 37, 0.06);
  color: #7a1f17;
}

.xml-notice-title {
  font-size: 0.88rem;
  font-weight: 800;
}

.xml-notice-pos {
  font-weight: 600;
  opacity: 0.85;
}

.xml-notice-detail {
  font: 0.82rem/1.55 "SFMono-Regular", "Cascadia Code", "Liberation Mono", monospace;
  margin: 6px 0 0;
  max-height: 160px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.xml-notice-sync {
  margin-top: 12px;
}

.xml-editor-shell {
  display: flex;
  flex: 1 1 auto;
  min-height: 560px;
  width: 100%;
}

.xml-preview-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.xml-preview-head {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-between;
}

.xml-preview-meta {
  align-items: baseline;
  display: flex;
  gap: 10px;
  min-width: 0;
}

.xml-preview-label {
  color: var(--shell-navy);
  font-size: 0.95rem;
  font-weight: 800;
}

.xml-preview-action {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.82rem;
}

.xml-preview-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.xml-output-empty {
  align-items: center;
  border: 1px dashed var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: rgba(15, 23, 35, 0.55);
  display: flex;
  font-size: 0.92rem;
  justify-content: center;
  min-height: 520px;
  padding: 18px;
  text-align: center;
}

@media (max-width: 599px) {
  .xml-toolbar-head,
  .xml-preview-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .xml-toolbar-block {
    min-width: 0;
    width: 100%;
  }
}
</style>
