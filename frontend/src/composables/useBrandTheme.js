import {
  applyBrandById,
  readStoredBrandId,
  writeStoredBrandId
} from 'src/design-system/themeCssVars'
import { DESIGN_SYSTEM_OPTIONS } from 'src/design-system/designSystemOptions'
import { DEFAULT_BRAND_ID, getBrandTokens } from 'src/design-system/tokens/brands'
import { computed, shallowRef } from 'vue'

const currentBrandId = shallowRef(DEFAULT_BRAND_ID)
let initialized = false

function ensureBrandTheme() {
  if (initialized) {
    return
  }

  const brandId = readStoredBrandId()
  currentBrandId.value = getBrandTokens(brandId).id
  applyBrandById(currentBrandId.value)
  initialized = true
}

function setBrandTheme(brandId) {
  const nextBrandId = getBrandTokens(brandId).id
  currentBrandId.value = nextBrandId
  applyBrandById(nextBrandId)
  writeStoredBrandId(nextBrandId)
}

export function useBrandTheme() {
  ensureBrandTheme()

  return {
    brandOptions: DESIGN_SYSTEM_OPTIONS,
    currentBrandId,
    currentBrand: computed(() => getBrandTokens(currentBrandId.value)),
    setBrandTheme
  }
}
