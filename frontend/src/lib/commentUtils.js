export function formatRelativeTime(input) {
  const date = input instanceof Date ? input : new Date(input)
  if (Number.isNaN(date.getTime())) return ''

  const diff = Date.now() - date.getTime()
  const sec = Math.floor(diff / 1000)
  if (sec < 30) return '刚刚'
  if (sec < 3600) return `${Math.floor(sec / 60)} 分钟前`
  if (sec < 86400) return `${Math.floor(sec / 3600)} 小时前`
  if (sec < 86400 * 30) return `${Math.floor(sec / 86400)} 天前`

  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const AVATAR_PALETTE = [
  '#d4a373', // warm tan
  '#bc8a64', // bronze
  '#a98467', // muted brown
  '#dda15e', // peach
  '#9c6644', // chocolate
  '#b08968', // taupe
  '#c08552', // copper
  '#7f5539', // espresso
  '#a47148', // mocha
  '#cbb279' // sand
]

export function avatarColorFor(name) {
  const text = (name || '').trim() || '?'
  let hash = 0
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) >>> 0
  }
  return AVATAR_PALETTE[hash % AVATAR_PALETTE.length]
}

export function avatarInitial(name) {
  const trimmed = (name || '').trim()
  if (!trimmed) return '?'
  // Prefer first character; handles surrogate pairs for emoji-only names.
  const it = trimmed[Symbol.iterator]()
  const { value } = it.next()
  return (value || '?').toUpperCase()
}
