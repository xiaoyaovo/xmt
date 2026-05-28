import presetRemToPx from '@unocss/preset-rem-to-px'
import { FileSystemIconLoader } from '@iconify/utils/lib/loader/node-loaders'
import { defineConfig, presetAttributify, presetIcons, presetUno } from 'unocss'

import { getIcons } from './build/index.js'

const icons = getIcons()
const brandColors = {
  accent: '#102542',
  'accent-hover': '#17345d',
  'accent-soft': 'rgba(16, 37, 66, 0.08)',
  accent2: '#ff7a59',
  highlight: '#c6ff6a',
  glow: 'rgba(198, 255, 106, 0.24)',
  surface: '#ffffff',
  'surface-2': '#eef3f8',
  text: '#0f1723',
  muted: '#5f6b7a',
  border: 'rgba(16, 37, 66, 0.12)'
}
const brandSafelist = [
  'brand-glass-panel',
  'brand-glass-panel-soft',
  'brand-editorial-kicker',
  'brand-editorial-title',
  'brand-body-copy',
  'brand-pill-button',
  'brand-primary-button',
  'brand-secondary-button',
  'brand-metric-card',
  'brand-grid-card',
  'brand-mesh-orb',
  'brand-grid-surface',
  'brand-hairline',
  'brand-outline-label',
  'brand-floating-grid',
  'brand-panel-inset'
]

export default defineConfig({
  content: {
    pipeline: {
      include: [
        /\.(vue|svelte|[jt]sx|mdx?|astro|elm|php|phtml|html)($|\?)/,
        'node_modules/@nuxt/ui/dist/**/*.{vue,js,mjs}'
      ]
    }
  },
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      warn: true,
      scale: 1.1,
      prefix: ['g-'],
      collections: {
        svg: FileSystemIconLoader('./src/assets/icons/svg')
      }
    }),
    presetRemToPx({ baseFontSize: 4 })
  ],
  safelist: [...icons, ...brandSafelist],
  shortcuts: [
    ['flex-center', 'flex items-center justify-center'],
    ['panel-shell', 'rounded-[var(--brand-radius-lg,24px)] border border-solid border-[var(--brand-color-border)] bg-[var(--brand-color-surface)]/75 shadow-[0_24px_80px_rgba(16,37,66,0.16)]'],
    ['tool-chip', 'rounded-[var(--brand-radius-pill,999px)] bg-[var(--brand-color-accent-soft)] px-12 py-8 text-[13px] font-700 text-[var(--brand-color-accent)]'],
    ['brand-glass-panel', 'relative overflow-hidden rounded-[var(--brand-radius-lg,24px)] border border-white/72 bg-white/72 shadow-[0_28px_90px_rgba(16,37,66,0.14)] backdrop-blur-[18px]'],
    ['brand-glass-panel-soft', 'relative overflow-hidden rounded-[var(--brand-radius-lg,24px)] border border-[rgba(16,37,66,0.08)] bg-white/72 shadow-[0_24px_70px_rgba(16,37,66,0.12)] backdrop-blur-[14px]'],
    ['brand-editorial-kicker', 'text-[12px] font-700 uppercase tracking-[0.22em] text-[rgba(16,37,66,0.58)]'],
    ['brand-editorial-title', 'font-[Georgia,Times_New_Roman,serif] text-[var(--brand-color-accent)] leading-[0.98] font-600'],
    ['brand-body-copy', 'text-[rgba(15,23,35,0.74)] leading-[1.76]'],
    ['brand-pill-button', 'inline-flex items-center justify-center rounded-[var(--brand-radius-pill,999px)] px-18 min-h-48 text-[15px] font-700 no-underline transition-all duration-180 ease-out'],
    ['brand-primary-button', 'brand-pill-button bg-[var(--brand-color-accent)] text-white shadow-[0_20px_36px_rgba(16,37,66,0.18)] hover:-translate-y-2 hover:bg-[var(--brand-color-accent-hover)] hover:shadow-[0_26px_42px_rgba(16,37,66,0.22)] focus-visible:outline-none focus-visible:-translate-y-2'],
    ['brand-secondary-button', 'brand-pill-button border border-[rgba(16,37,66,0.12)] bg-white/76 text-[var(--brand-color-accent)] hover:-translate-y-2 hover:border-[rgba(16,37,66,0.22)] hover:shadow-[0_18px_32px_rgba(16,37,66,0.10)] focus-visible:outline-none focus-visible:-translate-y-2'],
    ['brand-metric-card', 'rounded-[var(--brand-radius-md,16px)] border border-[rgba(16,37,66,0.08)] bg-white/70 p-18 shadow-[0_12px_30px_rgba(16,37,66,0.06)]'],
    ['brand-grid-card', 'brand-glass-panel-soft p-24 transition-transform duration-200 ease-out hover:-translate-y-6 hover:shadow-[0_30px_90px_rgba(16,37,66,0.16)]'],
    ['brand-mesh-orb', 'pointer-events-none absolute rounded-full opacity-18'],
    ['brand-grid-surface', 'relative isolate'],
    ['brand-hairline', 'absolute inset-x-0 top-0 h-1 bg-[var(--brand-color-accent2)] opacity-90'],
    ['brand-outline-label', 'inline-flex items-center gap-8 rounded-[var(--brand-radius-pill,999px)] border border-[rgba(16,37,66,0.08)] bg-white/64 px-12 py-8 text-[12px] font-700 tracking-[0.12em] uppercase text-[rgba(16,37,66,0.56)]'],
    ['brand-floating-grid', 'bg-transparent'],
    ['brand-panel-inset', 'rounded-[var(--brand-radius-lg,24px)] border border-white/70 bg-white/90']
  ],
  theme: {
    colors: {
      ...Object.fromEntries(
        Object.entries(brandColors).map(([key, value]) => [
          `brand-${key}`,
          `var(--brand-color-${key}, ${value})`
        ])
      )
    }
  }
})
