import { DEFAULT_BRAND_ID, getBrandTokens } from './tokens/brands'

export const BRAND_STORAGE_KEY = 'xinming.brand.theme'

export function buildBrandCssVars(tokens = getBrandTokens(DEFAULT_BRAND_ID)) {
  const vars = {}

  Object.entries(tokens.colors).forEach(([key, value]) => {
    vars[`--brand-color-${key}`] = value
  })

  Object.entries(tokens.borderRadius).forEach(([key, value]) => {
    vars[`--brand-radius-${key}`] = value
  })

  Object.entries(tokens.spacing).forEach(([key, value]) => {
    vars[`--brand-spacing-${key}`] = value
  })

  Object.entries(tokens.fontWeight).forEach(([key, value]) => {
    vars[`--brand-weight-${key}`] = value
  })

  vars['--brand-font-family'] = tokens.fontFamily

  if (tokens.boxShadow) {
    Object.entries(tokens.boxShadow).forEach(([key, value]) => {
      vars[`--brand-shadow-${key}`] = value
    })
  }

  return vars
}

export function applyBrandCssVars(target = document.documentElement, tokens = getBrandTokens(DEFAULT_BRAND_ID)) {
  const vars = buildBrandCssVars(tokens)
  Object.entries(vars).forEach(([name, value]) => {
    target.style.setProperty(name, value)
  })
}

export function readStoredBrandId() {
  if (typeof window === 'undefined') {
    return DEFAULT_BRAND_ID
  }

  return window.localStorage.getItem(BRAND_STORAGE_KEY) || DEFAULT_BRAND_ID
}

export function writeStoredBrandId(brandId) {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(BRAND_STORAGE_KEY, brandId)
}

export function applyBrandById(brandId = DEFAULT_BRAND_ID, target = document.documentElement) {
  const tokens = getBrandTokens(brandId)
  applyBrandCssVars(target, tokens)
  target.dataset.brandTheme = tokens.id
  return tokens
}
