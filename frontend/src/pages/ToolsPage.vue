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
    title: 'Draw.io',
    description: '从工具区进入全屏流程图或白板编辑器，保存由 Xinming 接管。',
    meta: '可用 · 全屏编辑、账号同步',
    to: '/tools/drawio'
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
