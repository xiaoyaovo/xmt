export const homeHero = {
  badge: '个人站点 · 工具实验室',
  title: '一处安放想法、工具与日常输出的地方。',
  description: '首页负责表达，工具页负责效率。同一套品牌主题，三类页面各自保留合适的节奏。'
}

export const heroAction = {
  label: '进入工具区',
  to: '/tools',
  tone: 'primary'
}

export const homeRows = [
  {
    index: 1,
    title: 'CSV 预览器',
    description: '上传 CSV 后在本地解析，快速检查字段、行数和表格内容；登录后可保存版本。',
    to: '/tools/csv'
  },
  {
    index: 2,
    title: 'Mermaid 编辑器',
    description: '选择流程图、时序图或甘特图示例，编辑源码后实时查看图表；支持账号同步与下载 SVG。',
    to: '/tools/mermaid'
  },
  {
    index: 3,
    title: 'Draw.io',
    description: '进入全屏流程图编辑器，编辑体验交给 draw.io，保存和历史交给 Xinming。',
    to: { path: '/tools/drawio/editor', query: { mode: 'diagram' } }
  },
  {
    index: 4,
    title: '白板',
    description: '使用 draw.io sketch 白板做自由草图、头脑风暴和移动端手写。',
    to: { path: '/tools/drawio/editor', query: { mode: 'whiteboard' } }
  }
]

export const aboutSection = {
  kicker: '关于这里',
  title: '保持克制，先把日常工具做扎实。',
  description: '不堆砌功能、不强迫登录、不做表演型动效。视觉系统使用统一的设计 token，新增页面不需要重新拼一套语言。'
}
