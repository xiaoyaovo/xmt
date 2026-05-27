<script setup>
import { onBeforeUnmount, onMounted, shallowRef, watch } from 'vue'

import {
  applyBrandTheme,
  brandThemeItems,
  readStoredBrandTheme,
  writeStoredBrandTheme
} from 'src/lib/brandThemes'

const COLOR_MODE_KEY = 'xinming-color-mode'

const brandTheme = shallowRef('editorial')
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
  brandTheme.value = readStoredBrandTheme()
  colorMode.value = window.localStorage.getItem(COLOR_MODE_KEY) || 'system'
  applyBrandTheme(brandTheme.value)
  applyColorMode()
  mediaQuery.addEventListener('change', handleSystemChange)
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', handleSystemChange)
})

watch(brandTheme, (value) => {
  const normalized = applyBrandTheme(value)
  brandTheme.value = normalized
  writeStoredBrandTheme(normalized)
})

watch(colorMode, (value) => {
  window.localStorage.setItem(COLOR_MODE_KEY, value)
  applyColorMode(value)
})
</script>

<template>
  <div class="theme-switcher">
    <label class="theme-switcher-field">
      <span class="theme-switcher-label">品牌主题</span>
      <USelect
        v-model="brandTheme"
        class="theme-switcher-select"
        :items="brandThemeItems"
        value-key="value"
        label-key="label"
        size="sm"
      />
    </label>

    <label class="theme-switcher-field">
      <span class="theme-switcher-label">系统主题</span>
      <USelect
        v-model="colorMode"
        class="theme-switcher-select theme-switcher-select-mode"
        :items="colorModeItems"
        value-key="value"
        label-key="label"
        size="sm"
      />
    </label>
  </div>
</template>

<style scoped>
.theme-switcher {
  align-items: center;
  display: inline-flex;
  gap: 14px;
}

.theme-switcher-field {
  align-items: center;
  display: inline-flex;
  gap: 8px;
}

.theme-switcher-label {
  color: var(--brand-color-muted, rgba(16, 37, 66, 0.54));
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
}

.theme-switcher-select {
  min-width: 126px;
}

.theme-switcher-select-mode {
  min-width: 118px;
}

@media (max-width: 1120px) {
  .theme-switcher-label {
    display: none;
  }
}
</style>
