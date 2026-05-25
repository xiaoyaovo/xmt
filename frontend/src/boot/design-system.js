import { applyBrandById, readStoredBrandId } from 'src/design-system/themeCssVars'

export default () => {
  applyBrandById(readStoredBrandId())
}
