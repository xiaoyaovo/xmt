<template>
  <div class="section-page">
    <div class="section-hero">
      <div>
        <div class="section-kicker">后台区 · 运营壳层</div>
        <h1 class="section-title">后台先保持安静、清楚、可扩展。</h1>
      </div>
      <p class="section-text">
        这里后续承载发布、审核和配置。视觉跟随品牌主题，但信息组织会更接近内部工作台。
      </p>
    </div>

    <div class="admin-grid">
      <article
        v-for="panel in panels"
        :key="panel.title"
        class="admin-card"
      >
        <div class="admin-card-label">{{ panel.label }}</div>
        <h2 class="admin-card-title">{{ panel.title }}</h2>
        <p class="admin-card-text">{{ panel.text }}</p>
        <div class="admin-card-footer">{{ panel.footer }}</div>
      </article>
    </div>

    <section class="dashboard-band">
      <article class="dashboard-card dashboard-card-wide">
        <div class="section-kicker">后台布局</div>
        <h2 class="content-title">一个为审核、发布和配置准备的内部工作台骨架。</h2>
        <p class="section-text">
          后续这里会承载概览卡片、最近活动、待处理事项和后台快捷入口。视觉 token 会统一，但交互策略仍以效率优先。
        </p>
      </article>

      <article class="dashboard-card">
        <div class="dashboard-stat">--</div>
        <div class="dashboard-label">评论待接入</div>
      </article>

      <article class="dashboard-card">
        <div class="dashboard-stat">--</div>
        <div class="dashboard-label">内容待接入</div>
      </article>
    </section>
  </div>
</template>

<script setup>
const panels = [
  {
    label: '评论',
    title: '审核队列占位',
    text: '未来用于承载评论审核、状态切换、批量操作与处理记录。',
    footer: '筛选 · 批量动作 · 状态流转'
  },
  {
    label: '内容',
    title: '发布台占位',
    text: '未来用于承载首页区块、文章、工具说明与发布相关配置。',
    footer: '草稿 · 发布说明 · 内容健康度'
  },
  {
    label: '系统',
    title: '站点配置占位',
    text: '未来用于承载导航、功能开关、集成配置与系统级设置。',
    footer: '开关 · 集成 · 导航结构'
  }
]
</script>
