export const primaryNavItems = [
  {
    label: '首页',
    caption: '站点总览与公开内容入口',
    to: '/',
    icon: 'i-g-svg:home',
    exact: true
  },
  {
    label: '工具',
    caption: '面向日常工作的交互式工具台',
    to: '/tools',
    icon: 'i-g-svg:tool'
  },
  {
    label: '后台',
    caption: '运营、发布与审核相关的内部区域',
    to: '/admin',
    icon: 'i-g-svg:admin'
  }
]

export const workspaceNavItems = [
  {
    label: '工具实验室',
    caption: 'Mermaid、CSV 和后续工具都会收敛到清晰的工作台里。',
    to: '/tools',
    icon: 'i-g-svg:tool',
    detail: 'Quasar 继续负责高密度输入、结果预览和多端壳层这类更偏应用层的体验。'
  },
  {
    label: '运营后台',
    caption: '发布流程、审核操作和站点控制能力保留在内部工作面里。',
    to: '/admin',
    icon: 'i-g-svg:admin',
    detail: '内部区域继续保留务实的后台交互方式，同时不把后台视觉带到公开站点里。'
  }
]
