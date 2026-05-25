import { request } from './http'
import { API_BASE_URL } from './http'

export function uploadCsvFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/csv/files', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function listCsvFiles() {
  return request.get('/csv/files')
}

export function getCsvFile(fileId) {
  return request.get(`/csv/files/${fileId}`)
}

export function getCsvRows(fileId, { offset = 0, limit = 200 } = {}) {
  return request.get(`/csv/files/${fileId}/rows`, {
    params: {
      offset,
      limit
    }
  })
}

export function deleteCsvFile(fileId) {
  return request.delete(`/csv/files/${fileId}`)
}

export function csvDownloadUrl(fileId) {
  return `${API_BASE_URL.replace(/\/$/, '')}/csv/files/${fileId}/download`
}
