<script setup>
import { onBeforeUnmount, onMounted, shallowRef, watch } from 'vue'

const COLOR_MODE_KEY = 'xinming-color-mode'
const colorMode = shallowRef('system')
const colorModeItems = [
  { label: '跟随系统', value: 'system' },
  { label: '浅色', value: 'light' },
  { label: '深色', value: 'dark' }
]

let mediaQuery = null

function resolveMode(value = colorMode.value) {
  if (value === 'system') {
    return mediaQuery?.matches ? 'dark' : 'light'
  }

  return value
}

function applyColorMode(value = colorMode.value) {
  document.documentElement.classList.toggle('dark', resolveMode(value) === 'dark')
}

function handleSystemChange() {
  if (colorMode.value === 'system') {
    applyColorMode()
  }
}

onMounted(() => {
  mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  colorMode.value = window.localStorage.getItem(COLOR_MODE_KEY) || 'system'
  applyColorMode()
  mediaQuery.addEventListener('change', handleSystemChange)
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', handleSystemChange)
})

watch(colorMode, (value) => {
  window.localStorage.setItem(COLOR_MODE_KEY, value)
  applyColorMode(value)
})
</script>

<template>
  <div class="theme-switcher">
    <span class="theme-switcher-label">系统主题</span>
    <select
      v-model="colorMode"
      class="theme-switcher-select"
    >
      <option
        v-for="item in colorModeItems"
        :key="item.value"
        :value="item.value"
      >
        {{ item.label }}
      </option>
    </select>
  </div>
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
  font: inherit;
  font-size: 0.86rem;
  font-weight: 750;
  min-height: 34px;
  min-width: 126px;
  padding: 0 28px 0 12px;
}
</style>
