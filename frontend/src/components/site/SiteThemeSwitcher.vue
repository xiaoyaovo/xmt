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
    <USelect
      v-model="colorMode"
      class="theme-switcher-select"
      :items="colorModeItems"
      value-key="value"
      label-key="label"
      size="sm"
    />
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
  text-transform: uppercase;
}

.theme-switcher-select {
  min-width: 126px;
}
</style>
