<template>
  <div class="section-page">
    <div class="section-hero">
      <div>
        <div class="section-kicker">工具区 · Quasar 工作台</div>
        <h1 class="section-title">选择一个工具，进入工作台。</h1>
      </div>
      <p class="section-text">
        这里放日常会反复使用的小工具。入口保持清楚，进入详情页后再展开输入、预览和导出动作。
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
        <h2 class="content-title">每个工具都按同一种操作节奏展开。</h2>
        <p class="section-text">
          列表页只负责快速进入；详情页负责把输入区、结果区和关键动作摆清楚。后续接入文件类工具时，也会沿用这套节奏。
        </p>
      </div>

      <div class="workspace-preview">
        <div class="workspace-pane">
          <div class="workspace-pane-title">输入区占位</div>
          <div class="workspace-pane-body workspace-pane-body-muted">
            编辑器、上传区或参数表单
          </div>
        </div>
        <div class="workspace-pane">
          <div class="workspace-pane-title">输出区占位</div>
          <div class="workspace-pane-body">
            预览画布、表格结果或导出内容
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
    title: 'Mermaid 编辑器',
    status: '占位',
    text: '图表源码编辑、实时预览和导出动作会放在同一个工作面里。',
    meta: '桌面双栏，移动端纵向堆叠。',
    action: '查看占位页',
    to: '/tools/mermaid'
  },
  {
    title: 'CSV 预览器',
    status: '占位',
    text: '上传文件后快速查看字段、行列结构和表格预览。',
    meta: '优先处理滚动、筛选和移动端阅读。',
    action: '查看占位页',
    to: '/tools/csv'
  },
  {
    title: '工具扩展位',
    status: '预留',
    text: '后续新增工具继续使用同一套入口、状态和操作节奏。',
    meta: '保持统一，不把每个工具做成孤岛。',
    action: '停留当前页',
    to: '/tools'
  }
]
</script>
