import { boot } from 'quasar/wrappers'
import ui from '@nuxt/ui/vue-plugin'

export default boot(({ app }) => {
  app.use(ui)
})
