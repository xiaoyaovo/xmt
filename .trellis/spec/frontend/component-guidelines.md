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

For tools with an editable source and rendered/read-only preview, use `ToolWorkbench.vue` so the page keeps one top toolbar and two lower panes (`source-title`, `preview-title`, `toolbar`, `source`, `preview`). Put save, archive, examples, and secondary controls in the toolbar slot; put the editor and preview content in the pane slots.

Keep tool pages concise. Toolbar copy should be labels, counts, statuses, and commands, not instructional paragraphs. Success toasts or inline confirmations should only appear when users need feedback beyond an obvious button state; error and destructive-action warnings should remain visible.

For tool history/archive sections that are not inside `ToolWorkbench.vue`, use `ToolArchivePanel.vue` for the shared login-checking, logged-out, authenticated header, refresh, and empty states. Keep item row rendering in page-level slots when metadata or row actions differ by tool.

For tool save/add-new sections that are not inside `ToolWorkbench.vue`, use `ToolSavePanel.vue` for the shared card shell, primary save action, optional save-as/new action, helper copy, and account sync prompt. Put tool-specific pickers, examples, status summaries, and secondary actions in slots. Keep save cards aligned across tools: the shared top line should read as a save surface (`保存` kicker, right-side archive/sync status). The kicker alone identifies the section — do NOT also render a redundant `<h2>云端存档</h2>` next to a `保存` or `历史` kicker; pick one label per section, not both.

`ToolWorkbench.vue`'s `source-title` and `preview-title` props default to empty and only render when set. Omit them when the pane's identity is already obvious from its content (a source textarea is a source pane, a rendered diagram is a preview pane). Pass them only when there is a real disambiguation need (e.g., a file name or active diagram label).

Workspace stats (row counts, sync time, character length, connection state) belong as **one** inline muted text line below the toolbar head — not as a 3- or 4-card stat grid. Stat-card chrome (`*-summary-grid`, `*-toolbar-stats`) inflates the toolbar without earning its space. Reserve cards for repeated items (history list rows) or genuinely separate surfaces, not for header decoration.

Empty / loading states inside a tool pane should be a single short muted sentence (e.g., `选择或拖入一个 CSV 文件`, `粘贴 Mermaid 源码以预览`), not a kicker + h2 block. The pane's surrounding context already tells the user where they are.

## Narrative Site Primitives

For new site pages outside tool workspaces (landing, tools index, about-style content), compose with the shared narrative primitives instead of rolling new section shells:

- `frontend/src/components/site/NarrativeSection.vue` — single-column section wrapper with a hairline top divider and optional kicker / title / description header. Two widths: `text` (~720px) for prose and short row lists, `container` (~960px) for the slightly wider grid-of-rows. Opt into scroll-reveal by adding `data-reveal` on inner elements (see `useScrollReveal` in hook guidelines).
- `frontend/src/components/site/NumberedRow.vue` — `01 — title — description — →` row primitive. Renders as `RouterLink` when `to` is set, plain `<a>` when `href` is set, otherwise a non-interactive `<div>`. Use this instead of card grids for landing-page entries (IndexPage tool list, ToolsPage list). Do not wrap rows in additional card containers.
- `frontend/src/components/tools/ToolPageHeader.vue` — slim top strip for tool pages with `← 工具` back link + kicker + title + actions slot. Sits above the `tool-detail-shell`; do not duplicate page-level kicker / title blocks inside the workspace.

## Page-Level Route Transition

`MainLayout.vue` wraps `<router-view>` in `<transition name="page-fade">` (fade + small translateY, 180ms in / 120ms out). The transition's CSS classes (`.page-fade-enter-*`, `.page-fade-leave-*`) MUST live in an unscoped `<style>` block on the layout — scoped styles will not match child route components. Key on `route.path` rather than the route component instance so that query-only changes don't reset editor state on tool pages. Honor `prefers-reduced-motion: reduce` by skipping the translate in that case.

## Accessibility

Use native semantic controls where possible:

- Buttons for actions.
- Anchors for navigation/download links.
- Labels around file inputs when building custom upload controls.
- `aria-label` and `aria-expanded` for icon/avatar menu triggers.
- `alt` text for user avatars.

Disabled controls should use the native `disabled` attribute when possible.

Every interactive primitive (links, buttons, row entries, chip buttons) must have a visible `:focus-visible` style — typically a brand-shadow ring like `box-shadow: var(--brand-shadow-focus, 0 0 0 3px rgba(...))`. When you override transitions under `@media (prefers-reduced-motion: reduce)`, keep the focus ring intact; reduced motion removes movement, not the focus affordance.

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
