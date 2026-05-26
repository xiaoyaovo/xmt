<script setup>
import { RouterLink } from 'vue-router'

import ToolPageHeader from 'src/components/tools/ToolPageHeader.vue'

const editorLinks = [
  {
    title: '打开 Draw.io',
    description: '进入全屏流程图编辑器，保存时由 Xinming 接管 XML 存档。',
    meta: '图表模式',
    to: { path: '/tools/drawio/editor', query: { mode: 'diagram' } }
  },
  {
    title: '打开白板',
    description: '使用 draw.io sketch UI，适合自由草图、头脑风暴和移动端手写场景。',
    meta: '白板模式',
    to: { path: '/tools/drawio/editor', query: { mode: 'whiteboard' } }
  }
]

const integrationSteps = [
  'XinmingTools 只提供入口与文件管理，不在普通工具页内嵌编辑器。',
  '全屏编辑页通过 iframe 加载自托管 draw.io，并用 postMessage 接管保存。',
  '当前 MVP 复用账号同步后端保存 XML，后续再演进为独立文件与版本历史。'
]
</script>

<template>
  <div class="tool-detail-page drawio-entry-page">
    <ToolPageHeader
      title="Draw.io"
      kicker="Draw.io · 全屏入口"
    />

    <section class="tool-detail-shell drawio-entry-shell">
      <div class="drawio-entry-layout">
        <section class="drawio-entry-panel">
          <div class="section-kicker">编辑器</div>
          <h2 class="drawio-entry-title">选择模式后进入全屏工作区。</h2>
          <p class="drawio-entry-copy">
            手机和平板端不再把 draw.io 嵌在普通页面里，避免外层滚动和画布拖拽互相抢手势。
          </p>

          <div class="drawio-entry-actions">
            <RouterLink
              v-for="link in editorLinks"
              :key="link.title"
              class="drawio-entry-link"
              :to="link.to"
            >
              <span class="drawio-entry-link-body">
                <span class="drawio-entry-link-title">{{ link.title }}</span>
                <span class="drawio-entry-link-description">{{ link.description }}</span>
                <span class="drawio-entry-link-meta">{{ link.meta }}</span>
              </span>
              <span
                class="drawio-entry-link-arrow"
                aria-hidden="true"
              >→</span>
            </RouterLink>
          </div>
        </section>

        <section class="drawio-entry-panel drawio-entry-plan">
          <div class="section-kicker">联动方案</div>
          <h2 class="drawio-entry-title">保存和历史归 Xinming 管。</h2>
          <ol class="drawio-plan-list">
            <li
              v-for="step in integrationSteps"
              :key="step"
              class="drawio-plan-item"
            >
              {{ step }}
            </li>
          </ol>
        </section>
      </div>
    </section>
  </div>
</template>

<style scoped>
.drawio-entry-shell {
  max-width: 1040px;
}

.drawio-entry-layout {
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr);
  margin-top: 28px;
}

.drawio-entry-panel {
  background: var(--shell-panel);
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: var(--brand-radius-lg, 24px);
  box-shadow: var(--brand-shadow-card, var(--shell-shadow));
  min-width: 0;
  padding: 22px;
}

.drawio-entry-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.35rem, 2.4vw, 2rem);
  font-weight: 600;
  line-height: 1.18;
  margin: 10px 0 0;
}

.drawio-entry-copy {
  color: rgba(15, 23, 35, 0.7);
  line-height: 1.7;
  margin: 12px 0 0;
}

.drawio-entry-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 22px;
}

.drawio-entry-link {
  align-items: center;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: inherit;
  display: grid;
  gap: 14px;
  grid-template-columns: minmax(0, 1fr) auto;
  min-height: 96px;
  padding: 16px 18px;
  text-decoration: none;
  transition: background-color 160ms ease, border-color 160ms ease;
}

.drawio-entry-link:hover,
.drawio-entry-link:focus-visible {
  background: #ffffff;
  border-color: rgba(16, 37, 66, 0.18);
}

.drawio-entry-link:focus-visible {
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.drawio-entry-link-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.drawio-entry-link-title {
  color: var(--shell-navy);
  font-size: 1rem;
  font-weight: 800;
}

.drawio-entry-link-description {
  color: rgba(15, 23, 35, 0.66);
  font-size: 0.92rem;
  line-height: 1.55;
}

.drawio-entry-link-meta {
  color: rgba(15, 23, 35, 0.5);
  font-size: 0.82rem;
  font-weight: 700;
}

.drawio-entry-link-arrow {
  color: var(--shell-navy);
  font-size: 1.5rem;
  font-weight: 800;
}

.drawio-plan-list {
  counter-reset: drawio-step;
  display: flex;
  flex-direction: column;
  gap: 12px;
  list-style: none;
  margin: 18px 0 0;
  padding: 0;
}

.drawio-plan-item {
  color: rgba(15, 23, 35, 0.72);
  display: grid;
  gap: 10px;
  grid-template-columns: 32px minmax(0, 1fr);
  line-height: 1.62;
}

.drawio-plan-item::before {
  align-items: center;
  aspect-ratio: 1;
  background: var(--brand-color-accent, #102542);
  border-radius: var(--brand-radius-pill, 999px);
  color: #ffffff;
  content: counter(drawio-step);
  counter-increment: drawio-step;
  display: inline-flex;
  font-size: 0.78rem;
  font-weight: 800;
  justify-content: center;
  margin-top: 2px;
  width: 28px;
}

@media (max-width: 900px) {
  .drawio-entry-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 599px) {
  .drawio-entry-panel {
    padding: 18px;
  }

  .drawio-entry-link {
    min-height: 0;
    padding: 14px;
  }
}
</style>
