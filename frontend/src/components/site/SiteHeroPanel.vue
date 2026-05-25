<script setup>
import { RouterLink } from 'vue-router'

defineProps({
  hero: {
    type: Object,
    required: true
  },
  actions: {
    type: Array,
    default: () => []
  },
  metrics: {
    type: Array,
    default: () => []
  },
  status: {
    type: Object,
    required: true
  },
  stacks: {
    type: Array,
    default: () => []
  }
})
</script>

<template>
  <section class="site-hero brand-grid-surface">
    <article class="site-hero-copy brand-glass-panel">
      <span class="brand-hairline" />

      <div class="site-hero-badge brand-outline-label">
        {{ hero.badge }}
      </div>

      <h1 class="site-hero-title brand-editorial-title">
        {{ hero.title }}
      </h1>

      <p class="site-hero-description brand-body-copy">
        {{ hero.description }}
      </p>

      <div class="site-hero-actions">
        <RouterLink
          v-for="action in actions"
          :key="action.to"
          :to="action.to"
          class="site-hero-action"
          :class="action.tone === 'primary' ? 'brand-primary-button' : 'brand-secondary-button'"
        >
          {{ action.label }}
        </RouterLink>
      </div>

      <div class="site-hero-metrics">
        <article
          v-for="metric in metrics"
          :key="metric.label"
          class="site-metric-card brand-metric-card"
        >
          <div class="site-metric-value">{{ metric.value }}</div>
          <div class="site-metric-label">{{ metric.label }}</div>
        </article>
      </div>
    </article>

    <aside class="site-hero-aside brand-glass-panel">
      <span class="brand-hairline" />

      <article class="site-status-card brand-panel-inset">
        <div class="site-status-label brand-editorial-kicker">{{ status.label }}</div>
        <div class="site-status-value">{{ status.value }}</div>
        <p class="site-status-text brand-body-copy">{{ status.text }}</p>
      </article>

      <div class="site-stack-grid">
        <article
          v-for="item in stacks"
          :key="item.label"
          class="site-stack-card brand-panel-inset"
        >
          <div class="site-status-label brand-editorial-kicker">{{ item.label }}</div>
          <div class="site-stack-value">{{ item.value }}</div>
          <p class="site-stack-text brand-body-copy">{{ item.text }}</p>
        </article>
      </div>
    </aside>
  </section>
</template>

<style scoped>
.site-hero {
  align-items: stretch;
  display: grid;
  gap: 22px;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.58fr);
  margin: 0 auto;
  max-width: 1160px;
}

.site-hero-copy {
  border-radius: var(--brand-radius-lg, 24px);
  padding: 30px;
}

.site-hero-aside {
  border-radius: var(--brand-radius-lg, 24px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
}

.site-hero-title {
  font-size: clamp(2.35rem, 4.6vw, 4.25rem);
  margin: 16px 0;
  max-width: 12ch;
  position: relative;
  text-wrap: balance;
}

.site-hero-description {
  font-size: 1.02rem;
  max-width: 60ch;
}

.site-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.site-hero-metrics {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 26px;
}

.site-metric-value,
.site-status-value,
.site-stack-value {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-weight: 700;
}

.site-metric-value {
  font-size: 1.72rem;
}

.site-metric-label {
  color: rgba(15, 23, 35, 0.62);
  line-height: 1.55;
  margin-top: 8px;
}

.site-status-value {
  font-size: 1.62rem;
  margin: 10px 0 8px;
}

.site-stack-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.site-stack-value {
  font-size: 1.2rem;
  margin: 10px 0 8px;
}

@media (max-width: 1023px) {
  .site-hero {
    grid-template-columns: 1fr;
  }

  .site-hero-title {
    max-width: 14ch;
  }
}

@media (max-width: 699px) {
  .site-hero-copy {
    padding: 22px;
  }

  .site-hero-aside {
    padding: 16px;
  }

  .site-hero-title {
    font-size: clamp(2.2rem, 12vw, 3.35rem);
    max-width: 10ch;
  }

  .site-hero-metrics,
  .site-stack-grid {
    grid-template-columns: 1fr;
  }
}
</style>
