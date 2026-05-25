const { existsSync } = require('node:fs')
const { join } = require('node:path')
const { execSync } = require('node:child_process')

const appVitePath = join(process.cwd(), 'node_modules', '@quasar', 'app-vite')
const hasQuasarConfig =
  existsSync(join(process.cwd(), 'quasar.config.js')) ||
  existsSync(join(process.cwd(), 'quasar.config.ts'))

if (hasQuasarConfig && existsSync(appVitePath)) {
  execSync('quasar prepare', { stdio: 'inherit' })
}
