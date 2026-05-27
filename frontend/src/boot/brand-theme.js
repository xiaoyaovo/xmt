import { boot } from 'quasar/wrappers'

import { applyBrandTheme, readStoredBrandTheme } from 'src/lib/brandThemes'

export default boot(() => {
  applyBrandTheme(readStoredBrandTheme())
})
