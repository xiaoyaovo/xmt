<script setup>
defineProps({
  heading: {
    type: Object,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<template>
  <section class="site-content-band">
    <div class="site-content-heading">
      <div class="site-content-kicker brand-outline-label">{{ heading.kicker }}</div>
      <h2 class="site-content-title brand-editorial-title">{{ heading.title }}</h2>
      <p class="site-content-description brand-body-copy">{{ heading.description }}</p>
    </div>

    <div class="site-content-grid">
      <article
        v-for="item in items"
        :key="item.title"
        class="site-content-card brand-grid-card"
      >
        <span class="brand-hairline" />
        <div class="site-content-tag brand-editorial-kicker">{{ item.tag }}</div>
        <h3 class="site-content-card-title">{{ item.title }}</h3>
        <p class="site-content-card-text brand-body-copy">{{ item.text }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.site-content-band {
  margin: 34px auto 0;
  max-width: 1160px;
}

.site-content-heading {
  display: grid;
  gap: 12px;
  margin-bottom: 18px;
  max-width: 700px;
}

.site-content-kicker {
  justify-self: start;
}

.site-content-title {
  font-size: clamp(1.9rem, 3.4vw, 2.8rem);
  margin: 0;
  max-width: 12ch;
}

.site-content-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.site-content-card {
  border-radius: var(--brand-radius-lg, 24px);
  min-height: 220px;
}

.site-content-card-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.55rem;
  font-weight: 600;
  line-height: 1.12;
  margin: 12px 0;
}

@media (max-width: 1023px) {
  .site-content-grid {
    grid-template-columns: 1fr;
  }

  .site-content-card {
    min-height: auto;
  }
}
</style>
