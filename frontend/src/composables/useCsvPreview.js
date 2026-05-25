import Papa from 'papaparse'
import { computed, shallowRef } from 'vue'

function normalizeHeader(row = []) {
  return row.map((value, index) => {
    const label = String(value ?? '').trim()
    return label || `Column ${index + 1}`
  })
}

function normalizeRows(rows = [], columnCount = 0) {
  return rows.map((row) => {
    if (!Array.isArray(row)) return []
    if (row.length >= columnCount) return row

    return [...row, ...Array.from({ length: columnCount - row.length }, () => '')]
  })
}

export function useCsvPreview({ maxErrors = 5 } = {}) {
  const selectedFile = shallowRef(null)
  const columns = shallowRef([])
  const rows = shallowRef([])
  const delimiter = shallowRef(',')
  const parseErrors = shallowRef([])
  const loading = shallowRef(false)
  const errorMessage = shallowRef('')

  const rowCount = computed(() => rows.value.length)

  const fileSummary = computed(() => {
    if (!selectedFile.value) return null

    return {
      original_filename: selectedFile.value.name,
      size: selectedFile.value.size,
      columns: columns.value,
      row_count: rowCount.value,
      delimiter: delimiter.value,
      source: 'local'
    }
  })

  function resetPreview() {
    selectedFile.value = null
    columns.value = []
    rows.value = []
    delimiter.value = ','
    parseErrors.value = []
    errorMessage.value = ''
    loading.value = false
  }

  async function previewFile(file) {
    if (!file) return null

    selectedFile.value = file
    columns.value = []
    rows.value = []
    parseErrors.value = []
    errorMessage.value = ''
    loading.value = true

    return new Promise((resolve) => {
      Papa.parse(file, {
        skipEmptyLines: 'greedy',
        worker: true,
        complete(results) {
          const parsedRows = Array.isArray(results.data) ? results.data : []
          const header = normalizeHeader(parsedRows[0] || [])
          const bodyRows = normalizeRows(parsedRows.slice(1), header.length)

          if (!header.length) {
            errorMessage.value = '没有读取到 CSV 表头，请检查文件内容。'
          }

          columns.value = header
          rows.value = bodyRows
          delimiter.value = results.meta?.delimiter || ','
          parseErrors.value = (results.errors || []).slice(0, maxErrors)
          loading.value = false

          resolve(fileSummary.value)
        },
        error(error) {
          errorMessage.value = error.message || 'CSV 解析失败，请检查文件格式。'
          loading.value = false
          resolve(null)
        }
      })
    })
  }

  return {
    selectedFile,
    columns,
    rows,
    rowCount,
    delimiter,
    parseErrors,
    loading,
    errorMessage,
    fileSummary,
    previewFile,
    resetPreview
  }
}
