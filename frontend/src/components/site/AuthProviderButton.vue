<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  caption: {
    type: String,
    required: true
  },
  mark: {
    type: String,
    required: true
  },
  busy: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])
</script>

<template>
  <UButton
    class="auth-provider-button"
    color="neutral"
    variant="ghost"
    type="button"
    :disabled="busy"
    :loading="busy"
    @click="emit('select')"
  >
    <span
      class="auth-provider-mark"
      aria-hidden="true"
    >
      {{ mark }}
    </span>
    <span class="auth-provider-copy">
      <span class="auth-provider-label">{{ label }}</span>
      <span class="auth-provider-caption">{{ caption }}</span>
    </span>
    <span
      class="auth-provider-arrow"
      aria-hidden="true"
    >
      →
    </span>
  </UButton>
</template>

<style scoped>
.auth-provider-button {
  align-items: center;
  background: var(--shell-panel);
  border: 1px solid var(--shell-line);
  border-radius: var(--brand-radius-md, 16px);
  color: var(--brand-color-text);
  cursor: pointer;
  display: grid;
  font: inherit;
  gap: 12px;
  grid-template-columns: auto minmax(0, 1fr) auto;
  min-height: 68px;
  padding: 12px;
  text-align: left;
  transition:
    background-color 160ms ease,
    border-color 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
  width: 100%;
}

.auth-provider-button:hover,
.auth-provider-button:focus-visible {
  background: var(--brand-color-surface, #ffffff);
  border-color: var(--brand-color-border, rgba(16, 37, 66, 0.2));
  box-shadow: var(--brand-shadow-card, 0 16px 34px rgba(16, 37, 66, 0.1));
  outline: none;
  transform: translateY(-1px);
}

.auth-provider-button:disabled {
  cursor: wait;
  opacity: 0.7;
  transform: none;
}

.auth-provider-mark {
  align-items: center;
  aspect-ratio: 1;
  background: var(--brand-color-accent-soft, rgba(16, 37, 66, 0.08));
  border-radius: var(--brand-radius-sm, 8px);
  color: var(--brand-color-text);
  display: inline-flex;
  font-size: 0.8rem;
  font-weight: 900;
  justify-content: center;
  width: 42px;
}

.auth-provider-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.auth-provider-label {
  font-size: 0.94rem;
  font-weight: 850;
}

.auth-provider-caption {
  color: var(--brand-color-muted, rgba(15, 23, 35, 0.58));
  font-size: 0.8rem;
  line-height: 1.45;
}

.auth-provider-arrow {
  color: var(--brand-color-muted, rgba(16, 37, 66, 0.42));
  font-weight: 900;
}

@media (prefers-reduced-motion: reduce) {
  .auth-provider-button {
    transition: none;
  }

  .auth-provider-button:hover,
  .auth-provider-button:focus-visible {
    transform: none;
  }
}
</style>
