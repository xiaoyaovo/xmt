<template>
  <div class="section-page">
    <div class="section-hero">
      <div>
        <div class="section-kicker">工具区 · Quasar 工作台</div>
        <h1 class="section-title">选择一个工具，直接进入工作台。</h1>
      </div>
      <p class="section-text">
        CSV、Mermaid 和 Draw.io demo 已经接入统一的工作台节奏：先输入或选择内容，再预览结果，最后按需保存、同步或导出。
      </p>
    </div>

    <div class="tool-grid">
      <article
        v-for="tool in tools"
        :key="tool.title"
        class="tool-card"
      >
        <div class="tool-status">{{ tool.status }}</div>
        <h2 class="tool-title">{{ tool.title }}</h2>
        <p class="tool-text">{{ tool.text }}</p>
        <div class="tool-meta">{{ tool.meta }}</div>
        <RouterLink
          class="tool-link"
          :to="tool.to"
        >
          {{ tool.action }}
        </RouterLink>
      </article>
    </div>

    <section class="workspace-panel">
      <div class="workspace-copy">
        <div class="section-kicker">工作台模式</div>
        <h2 class="content-title">进入后先处理内容，再看结果。</h2>
        <p class="section-text">
          列表页负责快速分流；详情页把输入、预览、历史和导出动作放在同一个视野里。未登录也能先完成本地预览，后续再接账号同步。
        </p>
      </div>

      <div class="workspace-preview">
        <div class="workspace-pane">
          <div class="workspace-pane-title">CSV 流程</div>
          <div class="workspace-pane-body workspace-pane-body-muted">
            上传文件 -> 浏览器解析 -> 表格分页 -> 保存历史
          </div>
        </div>
        <div class="workspace-pane">
          <div class="workspace-pane-title">图表流程</div>
          <div class="workspace-pane-body">
            选择示例 -> 编辑图形或源码 -> 保存 XML -> 导出
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const tools = [
  {
    title: 'Draw.io Demo',
    status: 'Demo',
    text: '通过 iframe embed 运行 diagrams.net，体验完整流程图和白板编辑器。',
    meta: '当前保存到页面内存，适合验证集成方式。',
    action: '查看 Demo',
    to: '/tools/drawio'
  },
  {
    title: 'Mermaid 编辑器',
    status: '可用',
    text: '选择流程图、时序图或甘特图示例，编辑源码后实时查看图表。',
    meta: '支持账号同步、复制源码和下载 SVG。',
    action: '进入 Mermaid',
    to: '/tools/mermaid'
  },
  {
    title: 'CSV 预览器',
    status: '可用',
    text: '上传 CSV 后在本地解析，快速检查字段、行数和表格内容。',
    meta: '登录后可保存历史，继续查看或下载原文件。',
    action: '进入 CSV',
    to: '/tools/csv'
  }
]
</script>
