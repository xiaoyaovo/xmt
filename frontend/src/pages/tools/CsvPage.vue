<script setup>
import Papa from 'papaparse'
import {
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger,
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
import ToolSaveDialog from 'src/components/tools/ToolSaveDialog.vue'
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
const historyOpen = shallowRef(false)
const saveDialogOpen = shallowRef(false)
const saveDialogDefaults = shallowRef({ title: '', remark: '' })
const dragActive = shallowRef(false)

const totalPages = computed(() => {
  if (!activeFile.value?.row_count) return 1
  return Math.max(1, Math.ceil(activeFile.value.row_count / rowsPerPage.value))
})

const offset = computed(() => (page.value - 1) * rowsPerPage.value)

const activeColumns = computed(() => activeFile.value?.columns || [])

const previewRows = computed(() => {
  return localPreview.rows.value.slice(offset.value, offset.value + rowsPerPage.value)
})

const savePanelStatus = computed(() => {
  if (uploading.value) return '保存中'
  if (loadingFiles.value) return '读取中'
  return ''
})

const saveMetaText = computed(() => {
  if (!activeFile.value) return ''
  const parts = []
  if (activeFile.value.row_count != null) parts.push(`${activeFile.value.row_count || 0} 行`)
  if (activeFile.value.size) parts.push(formatBytes(activeFile.value.size))
  return parts.join(' · ')
})

const archiveCountText = computed(() => {
  if (loadingFiles.value) return '读取中'
  return files.value.length ? String(files.value.length) : ''
})

const historyTriggerLabel = computed(() => {
  if (!auth.initialized || auth.loading) return '检查登录中'
  if (!auth.authenticated) return '未登录 · 登录后同步'
  if (loadingFiles.value) return '读取中'
  if (activeSource.value === 'history' && activeFile.value) {
    const fallback = activeFile.value.created_at ? formatDate(activeFile.value.created_at) : ''
    const activeLabel = (activeFile.value.title || '').trim()
      || activeFile.value.original_filename
      || fallback
    return `历史 · ${activeLabel}`
  }
  if (!files.value.length) return '无存档'
  return `历史存档 · ${files.value.length}`
})

function csvFileDisplayTitle(file) {
  return (file?.title || '').trim() || file?.original_filename || ''
}

function csvFileSecondaryLine(file) {
  const remark = (file?.remark || '').trim()
  const stamp = file?.created_at ? formatDate(file.created_at) : ''
  return remark ? `${remark} · ${stamp}` : stamp
}

const historyTriggerDisabled = computed(() => {
  if (!auth.initialized || auth.loading) return true
  if (!auth.authenticated) return true
  if (loadingFiles.value) return false
  return !files.value.length
})

const canSaveCsv = computed(() => Boolean(activeFile.value && activeColumns.value.length))

const csvTextPreview = computed(() => localPreview.sourceText.value)

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
    historyOpen.value = false
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

async function persistCsvVersion({ title = '', remark = '' } = {}) {
  if (!canSaveCsv.value) return

  if (!auth.authenticated) {
    accountSync.login()
    return
  }

  const editedFile = createCsvFileFromSource(createEditedFilename())
  uploading.value = true
  errorMessage.value = ''
  try {
    const uploaded = await uploadCsvFile(editedFile, { title, remark })
    await refreshFiles()
    await selectHistoryFile(uploaded)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    uploading.value = false
  }
}

async function saveLocalFile() {
  if (!canSaveCsv.value) return

  if (!auth.authenticated) {
    accountSync.login()
    return
  }

  const active = activeSource.value === 'history' ? activeFile.value : null
  saveDialogDefaults.value = {
    title: active?.title || '',
    remark: active?.remark || ''
  }
  saveDialogOpen.value = true
}

async function handleSaveDialogConfirm({ title, remark }) {
  await persistCsvVersion({ title, remark })
  saveDialogOpen.value = false
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
  if (!file?.id) return

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
  const nextValue = event.target.value
  localPreview.updateFromCsvText(nextValue)
  page.value = 1
  if (!nextValue.trim()) {
    localPreview.errorMessage.value = ''
  }
  if (!localPreview.columns.value.length) {
    activeFile.value = null
    activeSource.value = ''
    return
  }
  const file = localPreview.selectedFile.value
  if (file) {
    syncActiveFileFromPreview(file)
    return
  }
  activeFile.value = {
    id: null,
    original_filename: 'untitled.csv',
    size: new Blob([localPreview.sourceText.value]).size,
    columns: localPreview.columns.value,
    row_count: localPreview.rowCount.value,
    delimiter: localPreview.delimiter.value,
    source: 'local'
  }
  activeSource.value = 'local'
}

async function loadDroppedFile(file) {
  if (!file) return
  const isCsv = file.type === 'text/csv'
    || file.type === 'application/vnd.ms-excel'
    || /\.csv$/i.test(file.name || '')
  if (!isCsv) {
    errorMessage.value = '仅支持 .csv 文件'
    return
  }
  errorMessage.value = ''
  const preview = await localPreview.previewFile(file)
  if (preview) {
    activeFile.value = preview
    activeSource.value = 'local'
    page.value = 1
  }
}

function onDragEnter() {
  dragActive.value = true
}

function onDragOver() {
  dragActive.value = true
}

function onDragLeave() {
  dragActive.value = false
}

async function onDropFile(event) {
  dragActive.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    await loadDroppedFile(file)
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
              <span
                v-if="savePanelStatus"
                class="csv-toolbar-status"
              >{{ savePanelStatus }}</span>
            </div>

            <p
              v-if="saveMetaText"
              class="csv-save-meta"
            >{{ saveMetaText }}</p>

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

              <PopoverRoot v-model:open="historyOpen">
                <PopoverTrigger
                  class="csv-ghost-action csv-history-trigger"
                  :disabled="historyTriggerDisabled"
                  aria-label="历史存档"
                >
                  <span>{{ historyTriggerLabel }}</span>
                  <span
                    class="csv-history-trigger-caret"
                    aria-hidden="true"
                  >▾</span>
                </PopoverTrigger>

                <PopoverPortal>
                  <PopoverContent
                    class="csv-history-popover"
                    align="end"
                    :side-offset="8"
                  >
                    <div class="csv-history-popover-head">
                      <div class="csv-toolbar-head-left">
                        <div class="section-kicker">历史</div>
                        <span
                          v-if="archiveCountText"
                          class="csv-archive-count"
                        >· {{ archiveCountText }}</span>
                      </div>
                      <button
                        class="csv-ghost-action csv-history-refresh"
                        type="button"
                        :disabled="loadingFiles"
                        @click="refreshFiles"
                      >
                        {{ loadingFiles ? '刷新中' : '刷新' }}
                      </button>
                    </div>

                    <div
                      v-if="loadingFiles && !files.length"
                      class="csv-history-popover-empty"
                    >
                      读取中
                    </div>
                    <div
                      v-else-if="!files.length"
                      class="csv-history-popover-empty"
                    >
                      无存档
                    </div>
                    <div
                      v-else
                      class="csv-history-list"
                    >
                      <div
                        v-for="file in files"
                        :key="file.id"
                        class="csv-history-row"
                        :class="{ 'csv-history-row-active': activeSource === 'history' && activeFile?.id === file.id }"
                      >
                        <button
                          class="csv-history-open"
                          type="button"
                          @click="selectHistoryFile(file)"
                        >
                          <span class="csv-history-title">{{ csvFileDisplayTitle(file) }}</span>
                          <span class="csv-history-meta">{{ csvFileSecondaryLine(file) }}</span>
                        </button>
                        <button
                          class="csv-history-delete"
                          type="button"
                          :disabled="deletingId === file.id"
                          :aria-label="`删除 ${csvFileDisplayTitle(file)}`"
                          @click.stop="removeFile(file)"
                        >
                          {{ deletingId === file.id ? '...' : '×' }}
                        </button>
                      </div>
                    </div>
                  </PopoverContent>
                </PopoverPortal>
              </PopoverRoot>
            </div>

            <AccountSyncPanel
              class="csv-toolbar-sync"
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              @login="accountSync.login"
            />
          </section>
        </template>

        <template #source>
          <article
            class="csv-panel csv-edit-panel"
            :class="{ 'csv-edit-panel-drag': dragActive }"
          >
            <div
              v-if="errorMessage || localPreview.errorMessage.value"
              class="csv-notice csv-notice-error"
            >
              {{ errorMessage || localPreview.errorMessage.value }}
            </div>

            <div
              v-if="activeFile"
              class="csv-source-header"
            >
              <div class="csv-source-meta">
                <span class="csv-source-name">{{ activeFile.original_filename }}</span>
                <span class="csv-source-label">{{ sourceLabel }}</span>
              </div>
              <div
                v-if="activeSource === 'history'"
                class="csv-actions"
              >
                <a
                  class="csv-ghost-action"
                  :href="csvDownloadUrl(activeFile.id)"
                >
                  下载原文件
                </a>
                <button
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
              placeholder="粘贴 CSV 内容，或拖入 .csv 文件"
              aria-label="CSV 源码编辑器"
              spellcheck="false"
              @input="updateCsvText"
              @dragenter.prevent="onDragEnter"
              @dragover.prevent="onDragOver"
              @dragleave.prevent="onDragLeave"
              @drop.prevent="onDropFile"
            />
          </article>
        </template>

        <template #preview>
          <article class="csv-panel csv-preview-panel">
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

      <ToolSaveDialog
        v-model:open="saveDialogOpen"
        :default-title="saveDialogDefaults.title"
        :default-remark="saveDialogDefaults.remark"
        :busy="uploading"
        dialog-title="保存到云端存档"
        @confirm="handleSaveDialogConfirm"
      />
    </section>
  </div>
</template>

<style scoped>
.csv-panel {
  min-width: 0;
}

.csv-preview-panel,
.csv-edit-panel {
  min-height: 0;
}

.csv-edit-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.csv-source-header,
.csv-table-toolbar,
.csv-table-controls {
  align-items: center;
  display: flex;
  gap: 12px;
}

.csv-source-header,
.csv-table-toolbar {
  justify-content: space-between;
}

.csv-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

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
  flex: 1 1 100%;
}

.csv-history-trigger {
  display: inline-flex;
  max-width: 320px;
}

.csv-history-trigger > span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.csv-history-trigger-caret {
  font-size: 0.78rem;
  margin-left: 2px;
}

.csv-history-refresh {
  min-height: 32px;
  padding: 0 10px;
  font-size: 0.82rem;
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

.csv-toolbar-head-left {
  align-items: baseline;
  display: flex;
  gap: 6px;
}

.csv-archive-count {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
}

.csv-toolbar-status {
  text-align: right;
  overflow-wrap: anywhere;
}

.csv-save-meta {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.88rem;
  margin: 12px 0 0;
}

.csv-toolbar-actions {
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

.csv-primary-action:focus-visible,
.csv-ghost-action:focus-visible,
.csv-page-size-trigger:focus-visible,
.csv-file-picker:focus-within {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
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

.csv-table-toolbar {
  margin-top: 0;
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
  margin-top: 0;
  min-height: 560px;
  outline: none;
  padding: 18px;
  resize: vertical;
  transition: border-color 120ms ease, box-shadow 120ms ease;
  width: 100%;
}

.csv-text-editor:focus-visible {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.csv-text-editor::placeholder {
  color: rgba(237, 246, 255, 0.45);
}

.csv-edit-panel-drag .csv-text-editor {
  border-color: var(--brand-color-accent, #102542);
  box-shadow: inset 0 0 0 2px var(--brand-color-accent, #102542);
}

@media (prefers-reduced-motion: reduce) {
  .csv-text-editor {
    transition: none;
  }
}

.csv-loading {
  color: rgba(15, 23, 35, 0.62);
  margin-top: 14px;
}

@media (max-width: 599px) {
  .csv-source-header,
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

<style>
/* Unscoped: PopoverPortal teleports PopoverContent to <body>, so scoped
   selectors with data-v-XXX attributes do not reliably reach the
   portal-mounted subtree. These classes are namespaced enough not to leak. */
.csv-history-popover {
  background: #ffffff;
  border: 1px solid rgba(16, 37, 66, 0.1);
  border-radius: var(--brand-radius-md, 16px);
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16);
  color: var(--shell-navy, #102542);
  min-width: 320px;
  padding: 12px;
  z-index: 90;
}

.csv-history-popover:focus-visible {
  outline: none;
  box-shadow: 0 18px 42px rgba(16, 37, 66, 0.16), var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
}

.csv-history-popover-head {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.csv-history-popover-empty {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
  margin-top: 10px;
  padding: 6px 4px;
}

.csv-history-list {
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

.csv-history-list::-webkit-scrollbar {
  width: 8px;
}

.csv-history-list::-webkit-scrollbar-thumb {
  background: rgba(16, 37, 66, 0.2);
  border-radius: 999px;
}

.csv-history-row {
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

.csv-history-row:first-child {
  border-top: 0;
}

.csv-history-row:hover,
.csv-history-row:focus-within {
  background: rgba(16, 37, 66, 0.04);
}

.csv-history-row-active {
  background: rgba(16, 37, 66, 0.06);
  box-shadow: inset 3px 0 0 0 var(--brand-color-accent, #102542);
}

.csv-history-open {
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

.csv-history-open:focus-visible {
  border-radius: var(--brand-radius-sm, 8px);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.csv-history-title {
  color: var(--shell-navy, #102542);
  font-size: 0.88rem;
  font-weight: 700;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.csv-history-meta {
  color: rgba(15, 23, 35, 0.55);
  font-size: 0.8rem;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.csv-history-delete {
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

.csv-history-row:hover .csv-history-delete,
.csv-history-row:focus-within .csv-history-delete {
  color: var(--shell-coral, #ff7a59);
}

.csv-history-delete:hover {
  background: rgba(255, 122, 89, 0.12);
  color: var(--shell-coral, #ff7a59);
}

.csv-history-delete:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  color: var(--shell-coral, #ff7a59);
  outline: none;
}

.csv-history-delete:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
