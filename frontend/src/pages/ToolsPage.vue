<script setup>
import NarrativeSection from 'src/components/site/NarrativeSection.vue'
import NumberedRow from 'src/components/site/NumberedRow.vue'
import { useScrollReveal } from 'src/composables/useScrollReveal'

const { root } = useScrollReveal()

const tools = [
  {
    index: 1,
    title: 'CSV 预览器',
    description: '上传 CSV 后在本地解析，快速检查字段、行数和表格内容。',
    meta: '可用 · 支持云端保存',
    to: '/tools/csv'
  },
  {
    index: 2,
    title: 'Mermaid 编辑器',
    description: '选择流程图、时序图或甘特图示例，编辑源码后实时查看图表。',
    meta: '可用 · 支持账号同步、复制源码与下载 SVG',
    to: '/tools/mermaid'
  },
  {
    index: 3,
    title: 'LoL 战绩查询',
    description: '输入 Riot ID 查询段位和最近对局，支持国服外常见服务器。',
    meta: '可用 · Riot API 代理查询',
    to: '/tools/lol'
  },
  {
    index: 4,
    title: 'Draw.io',
    description: '直接进入全屏流程图编辑器，保存由 Xinming 接管。',
    meta: '可用 · 全屏图表、账号同步',
    to: { path: '/tools/drawio/editor', query: { mode: 'diagram' } }
  },
  {
    index: 5,
    title: '白板',
    description: '打开 draw.io 手绘风格白板，适合自由草图、头脑风暴和移动端手写。',
    meta: '可用 · 全屏白板、账号同步',
    to: { path: '/tools/drawio/editor', query: { mode: 'whiteboard' } }
  },
  {
    index: 6,
    title: 'XML 校验与格式化',
    description: '粘贴或拖入 XML，本地校验语法、按缩进美化或一键压缩。',
    meta: '可用 · 本地处理，不上传数据',
    to: '/tools/xml'
  }
]
</script>

<template>
  <div
    ref="root"
    class="tools-narrative"
  >
    <NarrativeSection
      :divider="false"
      width="container"
      kicker="工具区"
      title="选择一个工具，直接进入工作台。"
      description="先输入或选择内容，再预览结果，最后按需保存、同步或导出。未登录也能完成本地预览。"
    >
      <div class="tools-rows">
        <NumberedRow
          v-for="tool in tools"
          :key="tool.title"
          :index="tool.index"
          :title="tool.title"
          :description="tool.description"
          :meta="tool.meta"
          :to="tool.to"
        />
      </div>
    </NarrativeSection>
  </div>
</template>

<style scoped>
.tools-narrative {
  padding-bottom: 80px;
}

.tools-rows {
  display: flex;
  flex-direction: column;
  margin-top: 8px;
}
</style>
