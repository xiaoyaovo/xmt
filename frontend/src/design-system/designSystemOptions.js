import { BRAND_PRESETS, DEFAULT_BRAND_ID, getBrandTokens } from './tokens/brands'

export const DESIGN_SYSTEM_OPTIONS = BRAND_PRESETS

export function getDesignSystemOption(id = DEFAULT_BRAND_ID) {
  return DESIGN_SYSTEM_OPTIONS.find(option => option.id === id) || DESIGN_SYSTEM_OPTIONS[0]
}

export function resolveDesignSystemPreset(id = DEFAULT_BRAND_ID) {
  return getBrandTokens(id)
}
