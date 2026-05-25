<script setup>
defineProps({
  kicker: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  divider: {
    type: Boolean,
    default: true
  },
  reveal: {
    type: Boolean,
    default: true
  },
  width: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'container'].includes(value)
  }
})
</script>

<template>
  <section
    class="narrative-section"
    :class="[`narrative-width-${width}`, { 'narrative-no-divider': !divider }]"
  >
    <div
      class="narrative-inner"
      :data-reveal="reveal ? '' : null"
    >
      <header
        v-if="kicker || title || description || $slots.header"
        class="narrative-header"
      >
        <slot name="header">
          <div
            v-if="kicker"
            class="narrative-kicker"
          >
            {{ kicker }}
          </div>
          <h2
            v-if="title"
            class="narrative-title"
          >
            {{ title }}
          </h2>
          <p
            v-if="description"
            class="narrative-description"
          >
            {{ description }}
          </p>
        </slot>
      </header>

      <div class="narrative-body">
        <slot />
      </div>
    </div>
  </section>
</template>

<style scoped>
.narrative-section {
  border-top: 1px solid var(--shell-line);
  padding: 64px 20px;
}

.narrative-section:first-of-type,
.narrative-no-divider {
  border-top: none;
}

.narrative-inner {
  margin: 0 auto;
  max-width: 720px;
  opacity: 1;
  transform: none;
  transition:
    opacity 480ms cubic-bezier(0.22, 0.61, 0.36, 1),
    transform 480ms cubic-bezier(0.22, 0.61, 0.36, 1);
}

.narrative-inner[data-reveal] {
  opacity: 0;
  transform: translateY(14px);
  transition-delay: var(--reveal-delay, 0ms);
}

.narrative-inner[data-reveal].is-revealed {
  opacity: 1;
  transform: translateY(0);
}

.narrative-width-container .narrative-inner {
  max-width: 960px;
}

.narrative-header {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 36px;
}

.narrative-kicker {
  color: rgba(16, 37, 66, 0.62);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.narrative-title {
  color: var(--shell-navy);
  font-family: "Georgia", "Times New Roman", serif;
  font-size: clamp(1.7rem, 3.2vw, 2.4rem);
  font-weight: 600;
  line-height: 1.12;
  margin: 0;
  text-wrap: balance;
}

.narrative-description {
  color: rgba(15, 23, 35, 0.74);
  font-size: 1.02rem;
  line-height: 1.74;
  margin: 0;
  max-width: 60ch;
}

@media (prefers-reduced-motion: reduce) {
  .narrative-inner,
  .narrative-inner[data-reveal] {
    opacity: 1;
    transform: none;
    transition: none;
  }
}

@media (max-width: 599px) {
  .narrative-section {
    padding: 44px 16px;
  }

  .narrative-header {
    margin-bottom: 28px;
  }
}
</style>
