export const homeHero = {
  badge: '个人站点 · 工具实验室 · 运营后台',
  title: '个人站、工具台和后台，共用一套清晰界面。',
  description: '首页负责表达，工具页负责效率，后台负责管理。三类页面保留各自的使用节奏，同时共享同一套品牌主题。'
}

export const heroActions = [
  { label: '进入工具区', to: '/tools', tone: 'primary' },
  { label: '打开后台区', to: '/admin', tone: 'secondary' }
]

export const heroMetrics = [
  { value: '12', label: '可切换品牌主题' },
  { value: '03', label: '首页、工具、后台三类路由' },
  { value: '01', label: '统一的界面骨架' }
]

export const heroStatus = {
  label: '当前阶段',
  value: '界面骨架整理中',
  text: '先把导航、首页、工具入口和后台占位的布局收稳，再继续接入具体工具能力。'
}

export const heroStacks = [
  {
    label: '前台层',
    value: 'Reka UI',
    text: '用于导航、浮层和其他更需要品牌自由度的交互原语，不再沿用后台组件库的默认气质。'
  },
  {
    label: '工作台层',
    value: 'Quasar',
    text: '继续负责页面壳层、高密度表单，以及那些更依赖成熟多端能力的路由页面。'
  }
]

export const featureCards = [
  {
    index: '01',
    title: '公开页面更轻',
    text: '首页、内容页和个人介绍保留更强的排版感，但不再把大段说明堆成展示稿。'
  },
  {
    index: '02',
    title: '工具页面更像工作台',
    text: '工具区优先服务输入、预览、导出和结果检查，布局会比首页更克制、更好扫读。'
  },
  {
    index: '03',
    title: '主题变化真的落到组件',
    text: '颜色、圆角、阴影和字体都进入品牌变量，后续新增页面不用重新拼一套视觉语言。'
  }
]

export const contentHeading = {
  kicker: '系统分层',
  title: '三类页面，各自用更适合自己的交互方式。',
  description: '这个项目不需要再在“个人网站的表达感”和“应用型页面的实用性”之间二选一。不同路由可以使用更适合自己任务的组件体系。'
}

export const contentBlocks = [
  {
    tag: '公开站点',
    title: '首页展示、个人介绍、项目与内容页面',
    text: '这一层应该保持更强的表达感、排版感和轻量感。导航、浮层、提示和卡片现在都已经具备继续演进为设计系统的基础。'
  },
  {
    tag: '工具实验室',
    title: '像工作台一样构建的实用工具页面',
    text: '每个工具都可以继续保持输入区、输出区、说明区和导出动作这类实用布局，而不需要把公开站点的品牌表达硬塞进每一个高密度控件里。'
  },
  {
    tag: '运营后台',
    title: '内部发布、审核与配置相关的工作面',
    text: '后台页面依然保持结构化和务实，但视觉上已经回到同一套 token 体系下，而不是像另一个完全独立的产品。'
  }
]
