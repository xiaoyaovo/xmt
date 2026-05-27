<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  kicker: {
    type: String,
    default: ''
  },
  backTo: {
    type: [String, Object],
    default: '/tools'
  },
  backLabel: {
    type: String,
    default: '← 工具'
  }
})
</script>

<template>
  <header class="tool-page-strip">
    <UButton
      :to="backTo"
      class="tool-page-back"
      color="neutral"
      :label="backLabel"
      variant="subtle"
    />

    <div class="tool-page-title-block">
      <div
        v-if="kicker"
        class="tool-page-kicker"
      >
        {{ kicker }}
      </div>
      <h1 class="tool-page-title">{{ title }}</h1>
    </div>

    <div class="tool-page-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.tool-page-strip {
  align-items: center;
  border-bottom: 1px solid var(--shell-line);
  display: grid;
  gap: 16px;
  grid-template-columns: auto 1fr auto;
  margin: 0 auto;
  max-width: 1180px;
  padding: 18px 20px;
}

.tool-page-back {
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--shell-navy);
  display: inline-flex;
  font-size: 0.84rem;
  font-weight: 700;
  min-height: 34px;
  padding: 0 13px;
  text-decoration: none;
  transition: background-color 200ms ease, border-color 200ms ease;
}

.tool-page-back:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(16, 37, 66, 0.18);
}

.tool-page-back:focus-visible {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.16));
  outline: none;
}

.tool-page-title-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.tool-page-kicker {
  color: rgba(16, 37, 66, 0.6);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.tool-page-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: 1.4rem;
  font-weight: 600;
  line-height: 1.2;
  margin: 0;
}

.tool-page-actions {
  align-items: center;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

@media (max-width: 599px) {
  .tool-page-strip {
    gap: 12px;
    grid-template-columns: auto 1fr;
    padding: 14px 14px;
  }

  .tool-page-actions {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .tool-page-title {
    font-size: 1.2rem;
  }
}
</style>
