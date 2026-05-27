export const BRAND_THEME_KEY = 'xinming.brand.theme'
export const DEFAULT_BRAND_THEME = 'editorial'

export const brandThemeItems = [
  { label: '编辑感', value: 'editorial' },
  { label: '终端感', value: 'terminal' },
  { label: 'Apple 感', value: 'apple' },
  { label: 'Carbon 感', value: 'carbon' },
  { label: 'Fluent 感', value: 'fluent' },
  { label: 'Primer 感', value: 'primer' },
  { label: 'Stripe 感', value: 'stripe' },
  { label: 'Linear 感', value: 'linear' },
  { label: 'Material 感', value: 'material' },
  { label: 'Spotify 感', value: 'spotify' },
  { label: 'Claude 感', value: 'claude' },
  { label: 'Vercel 感', value: 'vercel' }
]

export function normalizeBrandTheme(value) {
  return brandThemeItems.some(item => item.value === value) ? value : DEFAULT_BRAND_THEME
}

export function readStoredBrandTheme() {
  if (typeof window === 'undefined') return DEFAULT_BRAND_THEME

  return normalizeBrandTheme(window.localStorage.getItem(BRAND_THEME_KEY))
}

export function writeStoredBrandTheme(value) {
  if (typeof window === 'undefined') return

  window.localStorage.setItem(BRAND_THEME_KEY, normalizeBrandTheme(value))
}

export function applyBrandTheme(value = DEFAULT_BRAND_THEME, target) {
  const normalized = normalizeBrandTheme(value)
  const nextTarget = target || (typeof document === 'undefined' ? null : document.documentElement)

  if (nextTarget) {
    nextTarget.dataset.brandTheme = normalized
  }

  return normalized
}
