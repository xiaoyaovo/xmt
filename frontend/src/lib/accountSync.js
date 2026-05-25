import { request } from './http'

export function listSyncItems(toolKey) {
  return request.get(`/sync/items/${toolKey}`)
}

export function getSyncItem(toolKey, itemKey) {
  return request.get(`/sync/items/${toolKey}/${itemKey}`)
}

export function saveSyncItem(toolKey, itemKey, { title = null, payload = {} } = {}) {
  return request.put(`/sync/items/${toolKey}/${itemKey}`, {
    title,
    payload
  })
}

export function deleteSyncItem(toolKey, itemKey) {
  return request.delete(`/sync/items/${toolKey}/${itemKey}`)
}
