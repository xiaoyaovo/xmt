import path from 'node:path'
import { globSync } from 'glob'

export function getIcons() {
  const svgFiles = globSync('src/assets/icons/svg/*.svg', {
    nodir: true,
    strict: false
  })

  return svgFiles.map((filePath) => {
    const fileName = path.basename(filePath)
    return `g-svg:${path.parse(fileName).name}`
  })
}
