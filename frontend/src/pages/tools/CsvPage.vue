<script setup>
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
const historyRows = shallowRef([])
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
  if (activeSource.value === 'local') {
    return localPreview.rows.value.slice(offset.value, offset.value + rowsPerPage.value)
  }

  return historyRows.value
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

const canSaveLocalFile = computed(() => activeSource.value === 'local' && localPreview.selectedFile.value)

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
  activeFile.value = file
  activeSource.value = 'history'
  page.value = 1
  await loadRows()
}

async function loadRows() {
  if (!activeFile.value) return

  loadingRows.value = true
  errorMessage.value = ''
  try {
    const response = await getCsvRows(activeFile.value.id, {
      offset: offset.value,
      limit: rowsPerPage.value
    })
    activeFile.value = response.file
    historyRows.value = response.rows
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loadingRows.value = false
  }
}

async function saveLocalFile() {
  if (!localPreview.selectedFile.value) return

  if (!auth.authenticated) {
    accountSync.login()
    return
  }

  uploading.value = true
  errorMessage.value = ''
  try {
    const uploaded = await uploadCsvFile(localPreview.selectedFile.value)
    await refreshFiles()
    await selectHistoryFile(uploaded)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    uploading.value = false
  }
}

async function handleFileInput(event) {
  const [file] = event.target.files || []
  if (file) {
    errorMessage.value = ''
    const preview = await localPreview.previewFile(file)
    if (preview) {
      activeFile.value = preview
      activeSource.value = 'local'
      historyRows.value = []
      page.value = 1
    }
  }
  event.target.value = ''
}

function clearLocalPreview() {
  localPreview.resetPreview()
  activeFile.value = null
  activeSource.value = ''
  historyRows.value = []
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
      historyRows.value = []
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
  if (activeSource.value === 'history') {
    await loadRows()
  }
}

async function changeRowsPerPage(value) {
  rowsPerPage.value = Number(value)
  page.value = 1
  if (activeSource.value === 'history') {
    await loadRows()
  }
}

onMounted(async () => {
  await auth.refreshMe()
  await refreshFiles()
})
</script>

<template>
  <div class="tool-detail-page csv-tool-page">
    <section class="tool-detail-shell">
      <div class="tool-detail-header">
        <div>
          <div class="section-kicker">CSV · 本地预览</div>
          <h1 class="section-title">先看清 CSV，再决定是否保存。</h1>
        </div>
        <p class="section-text">
          选择本地 CSV 后会直接在浏览器里解析预览。登录 GitHub 后，可以把文件保存到历史记录并在 30 天内继续查看。
        </p>
      </div>

      <section
        class="csv-workspace"
      >
        <aside class="csv-sidebar">
          <article class="csv-panel">
            <div class="csv-panel-topline">
              <div>
                <div class="section-kicker">上传</div>
                <h2 class="bench-title">添加 CSV 文件</h2>
              </div>
              <span class="csv-limit">20 MB</span>
            </div>

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
                {{ localPreview.loading.value ? '正在解析...' : '选择 CSV 文件' }}
              </span>
              <span class="csv-file-picker-caption">本地解析，不登录也可以预览</span>
            </label>

            <div class="csv-upload-actions">
              <button
                class="csv-primary-action"
                type="button"
                :disabled="!canSaveLocalFile || uploading || localPreview.loading.value"
                @click="saveLocalFile"
              >
                {{ uploading ? '保存中...' : auth.authenticated ? '保存到历史' : '登录后保存' }}
              </button>
              <button
                class="csv-ghost-action"
                type="button"
                :disabled="!activeFile || uploading || localPreview.loading.value"
                @click="clearLocalPreview"
              >
                清空预览
              </button>
            </div>
            <p class="csv-helper">
              本地预览不会上传文件。保存到历史需要 GitHub 登录，每个账号最多保留 50 个文件，总容量 500 MB。
            </p>
            <AccountSyncPanel
              :authenticated="accountSync.auth.authenticated"
              :loading="accountSync.auth.loading"
              :label="accountSync.syncLabel.value"
              description="登录后可把 CSV 文件保存到账号历史，后续继续预览和下载。"
              @login="accountSync.login"
            />
          </article>

          <article
            v-if="!auth.initialized || auth.loading"
            class="csv-panel csv-history-panel"
          >
            <div class="section-kicker">登录状态</div>
            <h2 class="bench-title">正在检查 GitHub 登录</h2>
            <p class="csv-helper">
              预览功能可直接使用，登录状态只影响历史记录。
            </p>
          </article>

          <article
            v-else-if="!auth.authenticated"
            class="csv-panel csv-history-panel"
          >
            <div class="section-kicker">历史</div>
            <h2 class="bench-title">登录后启用历史记录</h2>
            <p class="csv-helper">
              历史记录会绑定到你的 GitHub 账号，第一版不开放传统注册表单。
            </p>
            <button
              class="csv-primary-action csv-auth-action"
              type="button"
              :disabled="auth.loading"
              @click="accountSync.login"
            >
              {{ auth.loading ? '正在跳转...' : '使用 GitHub 登录' }}
            </button>
          </article>

          <article
            v-else
            class="csv-panel csv-history-panel"
          >
            <div class="csv-panel-topline">
              <div>
                <div class="section-kicker">历史</div>
                <h2 class="bench-title">最近文件</h2>
              </div>
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
              v-if="!files.length && !loadingFiles"
              class="csv-empty"
            >
              还没有 CSV 历史。
            </div>

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
          </article>
        </aside>

        <main class="csv-preview">
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
            <div class="section-kicker">预览</div>
            <h2 class="content-title">选择或上传一个 CSV 文件</h2>
            <p class="section-text">
              预览区会显示字段、统计信息和分页表格。
            </p>
          </article>

          <article
            v-else
            class="csv-panel csv-preview-panel"
          >
            <div class="csv-preview-header">
              <div>
                <div class="section-kicker">
                  {{ activeSource === 'local' ? '本地预览' : '历史文件' }}
                </div>
                <h2 class="csv-file-title">{{ activeFile.original_filename }}</h2>
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
              v-if="activeSource === 'local'"
              class="csv-notice"
            >
              当前展示的是浏览器本地解析结果，文件还没有上传。需要跨设备继续查看时，可以保存到历史。
            </div>

            <div
              v-if="localPreview.parseErrors.value.length"
              class="csv-notice csv-notice-warning"
            >
              已读取文件，但发现 {{ localPreview.parseErrors.value.length }} 条解析提示；表格会尽量展示可读取内容。
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
                    :key="`${activeSource}-${activeFile.id || activeFile.original_filename}-${offset + rowIndex}`"
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
        </main>
      </section>
    </section>
  </div>
</template>

<style scoped>
.csv-workspace {
  margin-top: 28px;
}

.csv-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
}

.csv-primary-action {
  border: 0;
  background: var(--brand-color-accent, #102542);
  border-radius: var(--brand-radius-pill, 999px);
  color: #ffffff;
  cursor: pointer;
  font: inherit;
  font-weight: 800;
  min-height: 46px;
  padding: 0 18px;
}

.csv-primary-action:disabled,
.csv-ghost-action:disabled,
.csv-file-picker-disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.csv-workspace {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(280px, 0.35fr) minmax(0, 0.65fr);
}

.csv-sidebar,
.csv-preview {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-width: 0;
}

.csv-panel {
  padding: 22px;
}

.csv-panel-topline,
.csv-preview-header,
.csv-table-toolbar,
.csv-table-controls,
.csv-actions {
  align-items: center;
  display: flex;
  gap: 12px;
}

.csv-panel-topline,
.csv-preview-header,
.csv-table-toolbar {
  justify-content: space-between;
}

.csv-limit,
.csv-helper,
.csv-history-meta,
.csv-empty,
.csv-table-toolbar {
  color: rgba(15, 23, 35, 0.62);
  font-size: 0.9rem;
}

.csv-file-picker {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  margin-top: 16px;
  padding: 16px;
}

.csv-file-input {
  height: 1px;
  opacity: 0;
  position: absolute;
  width: 1px;
}

.csv-file-picker-title {
  color: var(--shell-navy);
  font-weight: 800;
}

.csv-file-picker-caption {
  color: rgba(15, 23, 35, 0.58);
  font-size: 0.86rem;
}

.csv-upload-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.csv-auth-action {
  margin-top: 16px;
  width: 100%;
}

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

.csv-helper {
  line-height: 1.6;
  margin: 14px 0 0;
}

.csv-history-panel {
  max-height: 560px;
  overflow: auto;
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
  margin-top: 12px;
  padding: 14px;
  text-align: left;
  width: 100%;
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

.csv-loading {
  color: rgba(15, 23, 35, 0.62);
  margin-top: 14px;
}

@media (max-width: 1023px) {
  .csv-workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 599px) {
  .csv-panel {
    padding: 18px;
  }

  .csv-preview-header,
  .csv-table-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .csv-actions {
    flex-wrap: wrap;
  }
}
</style>
