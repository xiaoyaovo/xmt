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
- `frontend/src/components/tools/ToolArchivePanel.vue`
- `frontend/src/components/tools/ToolSavePanel.vue`
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

For tool history/archive sections, use `ToolArchivePanel.vue` for the shared login-checking, logged-out, authenticated header, refresh, and empty states. Keep item row rendering in page-level slots when metadata or row actions differ by tool.

For tool save/add-new sections, use `ToolSavePanel.vue` for the shared card shell, primary save action, optional save-as/new action, helper copy, and account sync prompt. Put tool-specific pickers, examples, status summaries, and secondary actions in slots. Keep save cards aligned across tools: the shared top line should read as a save surface (`保存` kicker, `云端存档` title, right-side archive/sync status), and tool state summaries should appear before picker/example controls when useful.

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

For iframe-based third-party editors, keep the iframe protocol boundary explicit in the page or a focused composable:

- Pin `postMessage` calls to the expected origin instead of `*`.
- Ignore messages whose `event.origin` does not match the configured editor origin.
- Parse message payloads defensively because editor protocols may return error payloads for unsupported actions.
- For diagrams.net/draw.io embed mode, load XML after the `init` event. To fetch the current XML from the host page, send `{ action: 'export', format: 'xml' }`; `save` is an editor-emitted event, not a host action.
- After the host app persists draw.io XML, send a `{ action: 'status', modified: false }` message back to the iframe so diagrams.net clears its unsaved-change state.

## Avoid

- Options API for new components.
- Component-level API calls when an existing `src/lib/` helper should be used.
- Unscoped global styles from feature components unless required for teleported content.
- Inline styles for theme values that already exist as CSS variables.
