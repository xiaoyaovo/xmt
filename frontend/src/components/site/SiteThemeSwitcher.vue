<script setup>
import { useBrandTheme } from 'src/composables/useBrandTheme'

const { brandOptions, currentBrandId, setBrandTheme } = useBrandTheme()
</script>

<template>
  <label class="theme-switcher">
    <span class="theme-switcher-label">品牌主题</span>
    <select
      class="theme-switcher-select"
      :value="currentBrandId"
      @change="setBrandTheme($event.target.value)"
    >
      <option
        v-for="option in brandOptions"
        :key="option.id"
        :value="option.id"
      >
        {{ option.name }}
      </option>
    </select>
  </label>
</template>

<style scoped>
.theme-switcher {
  align-items: center;
  display: inline-flex;
  gap: 10px;
}

.theme-switcher-label {
  color: rgba(16, 37, 66, 0.54);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.theme-switcher-select {
  appearance: none;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid var(--brand-color-border, rgba(16, 37, 66, 0.12));
  border-radius: var(--brand-radius-pill, 999px);
  color: var(--brand-color-accent, #102542);
  cursor: pointer;
  font-family: var(--brand-font-family, "Avenir Next", "Segoe UI", sans-serif);
  font-size: 0.92rem;
  font-weight: 700;
  min-height: 40px;
  max-width: 150px;
  padding: 0 30px 0 14px;
  text-overflow: ellipsis;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.theme-switcher-select:hover,
.theme-switcher-select:focus-visible {
  border-color: color-mix(in srgb, var(--brand-color-accent, #102542) 22%, transparent);
  box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(16, 37, 66, 0.12));
  outline: none;
  transform: translateY(-1px);
}
</style>
