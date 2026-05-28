const STORAGE_KEY = 'xmt:anon_id'

function generate() {
  if (typeof window === 'undefined') return ''
  const arr = new Uint8Array(16)
  window.crypto.getRandomValues(arr)
  return Array.from(arr, (b) => b.toString(36).padStart(2, '0')).join('')
}

export function getAnonId() {
  if (typeof window === 'undefined') return ''
  let id = ''
  try {
    id = window.localStorage.getItem(STORAGE_KEY) || ''
  } catch {
    id = ''
  }
  if (!id || id.length < 8 || id.length > 64 || !/^[A-Za-z0-9_-]+$/.test(id)) {
    id = generate()
    try {
      window.localStorage.setItem(STORAGE_KEY, id)
    } catch {
      // best-effort: privacy mode may block writes; keep in-memory value
    }
  }
  return id
}
