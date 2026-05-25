<script setup>
import Papa from 'papaparse'
import {
  SelectContent,
  SelectItem,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectViewport
} from 'reka-ui'
import { computed, onMounted, shallowRef } from 'vue'

import AccountSyncPanel from 'src/components/tools/AccountSyncPanel.vue'
import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'
import ToolWorkbench from 'src/components/tools/ToolWorkbench.vue'
import { useAccountSync } from 'src/composables/useAccountSync'
import { useCsvPreview } from 'src/composables/useCsvPreview'
import {
  csvDownloadUrl,
  deleteCsvFile,
  getCsvRows,
  listCsvFiles,
  uploadCsvFile
} from 'src/lib/csvFiles'
import { useAuthStore } from 'src/stores/auth'

const auth = useAuthStore()
const localPreview = useCsvPreview()
const accountSync = useAccountSync('csv')

const files = shallowRef([])
const activeFile = shallowRef(null)
const activeSource = shallowRef('')
const loadingFiles = shallowRef(false)
const loadingRows = shallowRef(false)
const uploading = shallowRef(false)
const deletingId = shallowRef(null)
const errorMessage = shallowRef('')
const page = shallowRef(1)
const rowsPerPage = shallowRef(200)
const rowsPerPageOptions = [200, 500, 1000]

const totalPages = computed(() => {
  if (!activeFile.value?.row_count) return 1
  return Math.max(1, Math.ceil(activeFile.value.row_count / rowsPerPage.value))
})

const offset = computed(() => (page.value - 1) * rowsPerPage.value)

const activeColumns = computed(() => activeFile.value?.columns || [])

const previewRows = computed(() => {
  return localPreview.rows.value.slice(offset.value, offset.value + rowsPerPage.value)
})

const fileStats = computed(() => {
  if (!activeFile.value) return []

  return [
    { label: '行数', value: activeFile.value.row_count },
    { label: '字段', value: activeFile.value.columns.length },
    { label: '大小', value: formatBytes(activeFile.value.size) },
    { label: '分隔符', value: activeFile.value.delimiter || ',' }
  ]
})

const savePanelStatus = computed(() => {
  if (uploading.value) return '保存中'
  if (loadingFiles.value) return '正在读取云端'
  if (!activeFile.value) return accountSync.syncLabel.value
  const parts = [
    activeFile.value.original_filename || '未命名',
    `${activeFile.value.row_count || 0} 行`,
    activeFile.value.size ? formatBytes(activeFile.value.size) : '0 B'
  ]
  if (localPreview.dirty.value) parts.push('待另存')
  else if (activeSource.value === 'history') parts.push('已保存')
  else if (activeSource.value === 'local') parts.push('待保存')
  return parts.join(' · ')
})

const canSaveCsv = computed(() => Boolean(activeFile.value && activeColumns.value.length))

const csvTextPreview = computed(() => {
  if (!activeFile.value) return ''
  return localPreview.sourceText.value
})

const sourceLabel = computed(() => {
  if (activeSource.value === 'history') return '云端存档'
  if (activeSource.value === 'local') return '本地文件'
  return '等待选择'
})

const saveButtonText = computed(() => {
  if (uploading.value) return '保存中...'
  if (!auth.authenticated) return '登录后保存'
  return localPreview.dirty.value ? '另存为新版本' : '保存为新版本'
})

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const value = bytes / 1024 ** exponent
  return `${value.toFixed(value >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`
}

function formatDate(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

async function refreshFiles() {
  if (!auth.authenticated) return

  loadingFiles.value = true
  errorMessage.value = ''
  try {
    const response = await listCsvFiles()
    files.value = response.items
    if (!activeFile.value && response.items.length) {
      await selectHistoryFile(response.items[0])
    }
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loadingFiles.value = false
  }
}

async function selectHistoryFile(file) {
  loadingRows.value = true
  errorMessage.value = ''
  try {
    const response = await loadAllHistoryRows(file)
    localPreview.selectedFile.value = new File([], file.original_filename, { type: file.content_type || 'text/csv' })
    localPreview.updateFromCsvText(Papa.unparse({
      fields: response.columns,
      data: response.rows
    }, {
      delimiter: file.delimiter || ',',
      newline: '\n'
    }))
    localPreview.dirty.value = false
    activeFile.value = response.file
    activeSource.value = 'history'
    page.value = 1
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loadingRows.value = false
  }
}

async function loadAllHistoryRows(file) {
  const limit = 1000
  let nextOffset = 0
  let latestFile = file
  let columns = file.columns || []
  const rows = []

  do {
    const response = await getCsvRows(file.id, {
      offset: nextOffset,
      limit
    })

    latestFile = response.file
    columns = response.columns || columns
    rows.push(...(response.rows || []))
    nextOffset += response.rows?.length || 0

    if (!response.has_more || !response.rows?.length) break
  } while (nextOffset < (latestFile.row_count || 0))

  return {
    file: latestFile,
    columns,
    rows
  }
}

function createEditedFilename() {
  const originalName = activeFile.value?.original_filename || localPreview.selectedFile.value?.name || 'edited.csv'
  const extensionIndex = originalName.toLowerCase().lastIndexOf('.csv')
  const baseName = extensionIndex > -1 ? originalName.slice(0, extensionIndex) : originalName
  const timestamp = new Date().toISOString().slice(0, 16).replace(/[-:T]/g, '')
  return `${baseName}-edited-${timestamp}.csv`
}

function syncActiveFileFromPreview(file) {
  const csvText = localPreview.toCsvText()
  activeFile.value = {
    ...(activeFile.value || {}),
    id: activeSource.value === 'history' ? activeFile.value?.id : null,
    original_filename: file.name,
    size: new Blob([csvText]).size,
    columns: localPreview.columns.value,
    row_count: localPreview.rowCount.value,
    delimiter: localPreview.delimiter.value,
    source: activeSource.value || 'local'
  }
}

function createCsvFileFromSource(filename) {
  const safeFilename = filename?.toLowerCase().endsWith('.csv') ? filename : `${filename || 'edited'}.csv`
  return new File([localPreview.sourceText.value], safeFilename, { type: 'text/csv;charset=utf-8' })
}

async function saveCsvVersion() {
  if (!canSaveCsv.value) return

  if (!auth.authenticated) {
    accountSync.login()
    return
  }

  const editedFile = createCsvFileFromSource(createEditedFilename())
  uploading.value = true
  errorMessage.value = ''
  try {
    const uploaded = await uploadCsvFile(editedFile)
    await refreshFiles()
    await selectHistoryFile(uploaded)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    uploading.value = false
  }
}

async function saveLocalFile() {
  await saveCsvVersion()
}

async function handleFileInput(event) {
  const [file] = event.target.files || []
  if (file) {
    errorMessage.value = ''
    const preview = await localPreview.previewFile(file)
    if (preview) {
      activeFile.value = preview
      activeSource.value = 'local'
      page.value = 1
    }
  }
  event.target.value = ''
}

function clearLocalPreview() {
  localPreview.resetPreview()
  activeFile.value = null
  activeSource.value = ''
  page.value = 1
}

async function removeFile(file) {
  if (activeSource.value !== 'history') return

  deletingId.value = file.id
  errorMessage.value = ''
  try {
    await deleteCsvFile(file.id)
    if (activeFile.value?.id === file.id) {
      activeFile.value = null
      activeSource.value = ''
      localPreview.resetPreview()
      page.value = 1
    }
    await refreshFiles()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    deletingId.value = null
  }
}

async function goToPage(nextPage) {
  page.value = Math.min(Math.max(nextPage, 1), totalPages.value)
}

async function changeRowsPerPage(value) {
  rowsPerPage.value = Number(value)
  page.value = 1
}

function updateCsvText(event) {
  localPreview.updateFromCsvText(event.target.value)
  page.value = 1
  if (localPreview.selectedFile.value) {
    syncActiveFileFromPreview(localPreview.selectedFile.value)
  }
}

onMounted(async () => {
  await auth.refreshMe()
  await refreshFiles()
})
</script>

<template>
  <div class="tool-detail-page csv-tool-page">
    <ToolPageHeader
      title="CSV"
      kicker="CSV · 表格预览"
    />

    <section class="tool-detail-shell">
      <ToolWorkbench>
        <template #toolbar>
          <section class="csv-toolbar-block csv-toolbar-save">
            <div class="csv-toolbar-head">
              <div class="section-kicker">保存</div>
              <span class="csv-toolbar-status">{{ savePanelStatus }}</span>
            </div>

            <div class="csv-toolbar-actions">
              <label
                class="csv-file-picker"
                :class="{ 'csv-file-picker-disabled': uploading || localPreview.loading.value }"
              >
                <input
                  class="csv-file-input"
                  type="file"
                  accept=".csv,text/csv"
                  :disabled="uploading || localPreview.loading.value"
                  @change="handleFileInput"
                >
                <span class="csv-file-picker-title">
                  {{ localPreview.loading.value ? '正在解析...' : '选择 CSV' }}
                </span>
              </label>
              <button
                class="csv-primary-action"
                type="button"
                :disabled="!canSaveCsv || uploading || localPreview.loading.value"
                @click="saveLocalFile"
              >
                {{ saveButtonText }}
              </button>
              <button
                class="csv-ghost-action"
                type="button"
                :disabled="!activeFile || uploading || localPreview.loading.value"
                @click="clearLocalPreview"
              >
                清空
              </button>
            </div>

            <AccountSyncPanel
              class="csv-toolbar-sync"
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              @login="accountSync.login"
            />
          </section>

          <section class="csv-toolbar-block csv-toolbar-archive">
            <div class="csv-toolbar-head">
              <div class="section-kicker">历史</div>
              <button
                class="csv-ghost-action"
                type="button"
                :disabled="loadingFiles"
                @click="refreshFiles"
              >
                {{ loadingFiles ? '刷新中' : '刷新' }}
              </button>
            </div>

            <div
              v-if="!auth.initialized || auth.loading"
              class="csv-toolbar-empty"
            >
              检查登录中
            </div>
            <div
              v-else-if="!auth.authenticated"
              class="csv-toolbar-empty"
            >
              未登录
            </div>
            <div
              v-else-if="!files.length && !loadingFiles"
              class="csv-toolbar-empty"
            >
              无存档
            </div>
            <div
              v-else
              class="csv-history-strip"
            >
              <button
                v-for="file in files"
                :key="file.id"
                class="csv-history-item"
                :class="{ 'csv-history-item-active': activeSource === 'history' && activeFile?.id === file.id }"
                type="button"
                @click="selectHistoryFile(file)"
              >
                <span class="csv-history-name">{{ file.original_filename }}</span>
                <span class="csv-history-meta">
                  {{ file.row_count }} 行 · {{ formatBytes(file.size) }} · {{ formatDate(file.created_at) }}
                </span>
              </button>
            </div>
          </section>
        </template>

        <template #source>
          <div
            v-if="errorMessage || localPreview.errorMessage.value"
            class="csv-notice csv-notice-error"
          >
            {{ errorMessage || localPreview.errorMessage.value }}
          </div>

          <article
            v-if="!activeFile"
            class="csv-panel csv-preview-empty"
          >
            <p class="csv-empty-hint">选择或拖入一个 CSV 文件</p>
          </article>

          <article
            v-else
            class="csv-panel csv-preview-panel"
          >
            <div class="csv-preview-header">
              <div class="csv-source-meta">
                <span class="csv-source-name">{{ activeFile.original_filename }}</span>
                <span class="csv-source-label">{{ sourceLabel }}</span>
              </div>
              <div class="csv-actions">
                <a
                  v-if="activeSource === 'history'"
                  class="csv-ghost-action"
                  :href="csvDownloadUrl(activeFile.id)"
                >
                  下载原文件
                </a>
                <button
                  v-if="activeSource === 'history'"
                  class="csv-ghost-action csv-danger-action"
                  type="button"
                  :disabled="deletingId === activeFile.id"
                  @click="removeFile(activeFile)"
                >
                  {{ deletingId === activeFile.id ? '删除中' : '删除' }}
                </button>
              </div>
            </div>

            <div
              v-if="localPreview.parseErrors.value.length"
              class="csv-notice csv-notice-warning"
            >
              解析提示：{{ localPreview.parseErrors.value.length }} 条
            </div>

            <textarea
              class="csv-text-editor"
              :value="csvTextPreview"
              aria-label="CSV 源码编辑器"
              spellcheck="false"
              @input="updateCsvText"
            />
          </article>
        </template>

        <template #preview>
          <article class="csv-panel csv-preview-panel">
            <div class="csv-preview-header">
              <div>
                <div class="section-kicker">表格</div>
                <h2 class="csv-file-title">CSV 预览</h2>
              </div>
              <span class="csv-table-toolbar">{{ localPreview.dirty.value ? '有未保存编辑' : '已同步' }}</span>
            </div>

            <div class="csv-summary-grid">
              <div
                v-for="item in fileStats"
                :key="item.label"
                class="csv-summary-card"
              >
                <div class="csv-summary-value">{{ item.value }}</div>
                <div class="csv-summary-label">{{ item.label }}</div>
              </div>
            </div>

            <div class="csv-chip-row">
              <span
                v-for="column in activeColumns"
                :key="column"
                class="csv-chip"
              >
                {{ column }}
              </span>
            </div>

            <div class="csv-table-toolbar">
              <span>第 {{ page }} / {{ totalPages }} 页</span>
              <div class="csv-table-controls">
                <SelectRoot
                  :model-value="String(rowsPerPage)"
                  @update:model-value="changeRowsPerPage"
                >
                  <SelectTrigger
                    class="csv-page-size-trigger"
                    aria-label="每页行数"
                  >
                    <SelectValue :placeholder="`${rowsPerPage} 行/页`" />
                    <span aria-hidden="true">/</span>
                  </SelectTrigger>

                  <SelectPortal>
                    <SelectContent
                      class="csv-page-size-content"
                      position="popper"
                      :side-offset="8"
                    >
                      <SelectViewport class="csv-page-size-viewport">
                        <SelectItem
                          v-for="option in rowsPerPageOptions"
                          :key="option"
                          class="csv-page-size-item"
                          :value="String(option)"
                        >
                          <SelectItemText>{{ option }} 行/页</SelectItemText>
                        </SelectItem>
                      </SelectViewport>
                    </SelectContent>
                  </SelectPortal>
                </SelectRoot>
                <button
                  class="csv-ghost-action"
                  type="button"
                  :disabled="page <= 1 || loadingRows"
                  @click="goToPage(page - 1)"
                >
                  上一页
                </button>
                <button
                  class="csv-ghost-action"
                  type="button"
                  :disabled="page >= totalPages || loadingRows"
                  @click="goToPage(page + 1)"
                >
                  下一页
                </button>
              </div>
            </div>

            <div class="csv-table-wrap">
              <table class="csv-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th
                      v-for="column in activeColumns"
                      :key="column"
                    >
                      {{ column }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(row, rowIndex) in previewRows"
                    :key="`${activeSource}-${activeFile?.id || activeFile?.original_filename || 'csv'}-${offset + rowIndex}`"
                  >
                    <td>{{ offset + rowIndex + 1 }}</td>
                    <td
                      v-for="(column, columnIndex) in activeColumns"
                      :key="`${column}-${columnIndex}`"
                    >
                      {{ row[columnIndex] ?? '' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div
              v-if="loadingRows"
              class="csv-loading"
            >
              正在读取数据...
            </div>
          </article>
        </template>
      </ToolWorkbench>
    </section>
  </div>
</template>

<style scoped>
.csv-panel {
  min-width: 0;
}

.csv-preview-panel,
.csv-preview-empty {
  min-height: 0;
}

.csv-preview-header,
.csv-table-toolbar,
.csv-table-controls {
  align-items: center;
  display: flex;
  gap: 12px;
}

.csv-preview-header,
.csv-table-toolbar {
  justify-content: space-between;
}

.csv-history-meta,
.csv-toolbar-empty,
.csv-toolbar-status,
.csv-table-toolbar {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.csv-toolbar-block {
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  min-width: 280px;
  padding: 14px;
}

.csv-toolbar-save {
  flex: 1.1 1 420px;
}

.csv-toolbar-archive {
  flex: 1 1 360px;
}

.csv-toolbar-head,
.csv-toolbar-actions {
  align-items: center;
  display: flex;
  gap: 12px;
}

.csv-toolbar-head {
  justify-content: space-between;
}

.csv-toolbar-status {
  text-align: right;
  overflow-wrap: anywhere;
}

.csv-toolbar-actions,
.csv-history-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.csv-toolbar-sync {
  margin-top: 12px;
}

.csv-source-meta {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 10px;
  min-width: 0;
}

.csv-source-name {
  color: var(--shell-navy);
  font-weight: 800;
  font-size: 0.95rem;
  overflow-wrap: anywhere;
}

.csv-source-label {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.82rem;
}

.csv-empty-hint {
  color: rgba(15, 23, 35, 0.6);
  font-size: 0.95rem;
  margin: 0;
}

.csv-toolbar-empty {
  background: rgba(255, 255, 255, 0.54);
  border: 1px dashed rgba(16, 37, 66, 0.16);
  border-radius: var(--brand-radius-md, 16px);
  margin-top: 12px;
  padding: 12px;
}

.csv-file-picker {
  cursor: pointer;
  display: inline-flex;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-pill, 999px);
  min-height: 38px;
  padding: 0 13px;
}

.csv-file-input {
  height: 1px;
  opacity: 0;
  position: absolute;
  width: 1px;
}

.csv-file-picker-title {
  align-items: center;
  color: var(--shell-navy);
  display: inline-flex;
  font-size: 0.88rem;
  font-weight: 800;
}

.csv-primary-action,
.csv-ghost-action,
.csv-page-size-trigger {
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

.csv-primary-action {
  background: var(--brand-color-accent, #102542);
  border-color: var(--brand-color-accent, #102542);
  color: #ffffff;
}

.csv-primary-action:disabled,
.csv-ghost-action:disabled,
.csv-file-picker-disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.csv-ghost-action:hover,
.csv-page-size-trigger:hover,
.csv-page-size-trigger[data-state='open'] {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(16, 37, 66, 0.18);
}

.csv-danger-action {
  color: #9b2f25;
}

.csv-notice-warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.2);
}

.csv-page-size-content {
  background: rgba(250, 252, 255, 0.98);
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  color: var(--shell-navy);
  min-width: 132px;
  padding: 6px;
  z-index: 90;
}

.csv-page-size-item {
  border-radius: var(--brand-radius-sm, 12px);
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 800;
  outline: none;
  padding: 9px 10px;
}

.csv-page-size-item[data-highlighted] {
  background: rgba(16, 37, 66, 0.07);
}

.csv-history-item {
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: inherit;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  text-align: left;
  width: min(260px, 100%);
}

.csv-history-item-active {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
}

.csv-history-name,
.csv-file-title {
  color: var(--shell-navy);
  font-weight: 800;
}

.csv-file-title {
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.4rem, 2.5vw, 2rem);
  margin: 8px 0 0;
  overflow-wrap: anywhere;
}

.csv-preview-empty {
  min-height: 340px;
}

.csv-summary-grid {
  margin-top: 18px;
}

.csv-chip-row {
  margin-top: 18px;
  max-height: 96px;
  overflow: auto;
}

.csv-table-toolbar {
  margin-top: 20px;
}

.csv-table-controls {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.csv-table-wrap {
  margin-top: 14px;
  overflow: auto;
}

.csv-table th:first-child,
.csv-table td:first-child {
  color: rgba(15, 23, 35, 0.48);
  font-weight: 700;
  min-width: 64px;
  position: sticky;
  left: 0;
  z-index: 1;
}

.csv-table td:first-child {
  background: rgba(255, 255, 255, 0.96);
}

.csv-text-editor {
  background: #0f1723;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--brand-radius-md, 16px);
  color: #edf6ff;
  font: 0.9rem/1.65 "SFMono-Regular", "Cascadia Code", "Liberation Mono", monospace;
  margin-top: 16px;
  min-height: 560px;
  outline: none;
  padding: 18px;
  resize: vertical;
  width: 100%;
}

.csv-loading {
  color: rgba(15, 23, 35, 0.62);
  margin-top: 14px;
}

@media (max-width: 599px) {
  .csv-preview-header,
  .csv-table-toolbar,
  .csv-toolbar-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .csv-toolbar-block {
    min-width: 0;
    width: 100%;
  }
}
</style>
