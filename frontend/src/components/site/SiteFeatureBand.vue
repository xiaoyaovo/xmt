<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<template>
  <section class="site-feature-band">
    <article
      v-for="item in items"
      :key="item.title"
      class="site-feature-card brand-grid-card"
    >
      <span class="brand-hairline" />
      <div class="site-feature-index">{{ item.index }}</div>
      <h2 class="site-feature-title">{{ item.title }}</h2>
      <p class="site-feature-text">{{ item.text }}</p>
    </article>
  </section>
</template>

<style scoped>
.site-feature-band {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: 22px auto 0;
  max-width: 1160px;
}

.site-feature-card {
  border-radius: var(--brand-radius-lg, 24px);
  min-height: 220px;
}

.site-feature-index {
  color: var(--shell-coral);
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.site-feature-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.24rem;
  font-weight: 600;
  line-height: 1.25;
  margin: 16px 0 12px;
}

.site-feature-text {
  color: rgba(15, 23, 35, 0.72);
  line-height: 1.74;
  margin: 0;
}

@media (max-width: 1023px) {
  .site-feature-band {
    grid-template-columns: 1fr;
  }

  .site-feature-card {
    min-height: auto;
  }
}
</style>
