# Frontend Component Guidelines

Vue components use single-file components with `<script setup>`, JavaScript, scoped styles where component-specific, and global styles only for app-wide shell or design primitives.

## Component Shape

Use this order for SFCs:

1. `<script setup>`
2. `<template>`
3. `<style scoped>` for local styles
4. Optional non-scoped `<style>` only when styling teleported third-party content

Reference examples:

- `frontend/src/components/tools/AccountSyncPanel.vue`
- `frontend/src/components/site/SiteUserMenu.vue`
- `frontend/src/pages/tools/MermaidPage.vue`

## Props And Events

Use `defineProps()` with runtime prop validation in JavaScript components. Required props should be marked explicitly.

Use `defineEmits()` for component events and emit semantic events, not DOM-specific implementation details. `AccountSyncPanel.vue` emits `login`; it does not know how the auth flow works.

When a component needs a prop object, access it through a named `props` binding if the template needs nested fields repeatedly, as in `SiteUserMenu.vue`.

## Local State

Use Vue refs from `<script setup>`:

- `shallowRef()` for objects, arrays, and UI state that is replaced wholesale.
- `computed()` for derived labels, booleans, and summary lists.
- `watch()` for side effects such as debounced Mermaid rendering.

Keep route/page orchestration in the page component. Extract reusable stateful logic into a composable when another page can use it or when it owns a clear capability.

## UI And Styling

Use existing CSS variables before adding new colors or radii:

- `--shell-*` variables from `src/css/app.scss`
- `--brand-color-*`, `--brand-radius-*`, `--brand-shadow-*` from the design system

Local component styles should use stable class names and responsive media queries. The current UI favors dense, tool-like panels and restrained visual styling over marketing-page ornamentation on tool pages.

Avoid nested card-like containers unless they represent genuinely separate repeated items or overlays. Keep tool workspaces structured with panels, sidebars, and main content areas like `CsvPage.vue` and `MermaidPage.vue`.

## Accessibility

Use native semantic controls where possible:

- Buttons for actions.
- Anchors for navigation/download links.
- Labels around file inputs when building custom upload controls.
- `aria-label` and `aria-expanded` for icon/avatar menu triggers.
- `alt` text for user avatars.

Disabled controls should use the native `disabled` attribute when possible.

## Third-Party UI

Reka UI primitives are used for hover cards and selects. Keep imported primitives at the top of `<script setup>` and wrap them in project classes so styles remain local to this app.

## Avoid

- Options API for new components.
- Component-level API calls when an existing `src/lib/` helper should be used.
- Unscoped global styles from feature components unless required for teleported content.
- Inline styles for theme values that already exist as CSS variables.
