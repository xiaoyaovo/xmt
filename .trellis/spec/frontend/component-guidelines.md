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

For account entry points, route users through the unified `/login` page instead of hardcoding a single
provider button in shell or tool components. Provider-specific buttons belong on `LoginPage.vue`; shell and
tool prompts should use generic copy such as `登录` / `打开登录页`.

For tool save/add-new sections that are not inside `ToolWorkbench.vue`, use `ToolSavePanel.vue` for the shared card shell, primary save action, optional save-as/new action, helper copy, and account sync prompt. Put tool-specific pickers, examples, status summaries, and secondary actions in slots. Keep save cards aligned across tools: the shared top line should read as a save surface (`保存` kicker, right-side archive/sync status). The kicker alone identifies the section — do NOT also render a redundant `<h2>云端存档</h2>` next to a `保存` or `历史` kicker; pick one label per section, not both.

For the actual "save with metadata" UX (collecting an archive name + remark from the user before persisting), use `frontend/src/components/tools/ToolSaveDialog.vue` rather than rolling per-tool inline forms. It is a Nuxt UI modal wrapper with:
- `v-model:open` (boolean)
- Props: `defaultTitle` (string), `defaultRemark` (string), `dialogTitle` (override), `dialogDescription`, `busy`
- Emits: `update:open`, `confirm({ title: string, remark: string })` (trimmed; empty strings allowed → backend treats as null), `cancel`

Open the dialog from the `保存` / `另存为新存档` button, pre-populating `defaultTitle` / `defaultRemark` with the active archive's existing values in overwrite mode, or empty strings in save-as-new mode. On `confirm`, call the existing persist function with the entered values. Both fields are always optional — never enforce required input.

When a trigger label (`*-history-trigger`, `*-save-trigger`, etc.) can display user-supplied text, cap it: `max-width: 320px` on the trigger plus `overflow: hidden; text-overflow: ellipsis; white-space: nowrap` on the inner label span. Otherwise a 100-char user title pushes neighboring toolbar buttons off the row. This applies whenever the label content is not under the developer's control.

**Don't gate the editing surface on whether a backing resource exists.** A tool's primary content-entry surface (textarea, canvas, editor) should always be mounted and usable, even before the user uploads / selects / creates a resource. Empty state lives inside the surface as a `placeholder` or muted hint, not as a separate "please upload first" card. When the user starts producing content without a backing resource, synthesize a local placeholder (`activeFile = { original_filename: 'untitled.csv', source: 'local', ... }`) so downstream code paths — save dialog, filename derivation, action enablement — keep working uniformly. The synthetic descriptor is cleared when the user empties the surface OR overwritten when a real upload/selection happens. See `CsvPage.vue#updateCsvText` for the canonical implementation.

**Drop-to-ingest on text editors.** When a `<textarea>` or contenteditable surface accepts files (CSV, Markdown, etc.), wire `@dragenter.prevent / @dragover.prevent / @dragleave.prevent / @drop.prevent` on the element. Toggle a `dragActive` ref on enter/leave; bind it to a class that applies an accent-border + inset glow using brand tokens (`var(--brand-color-accent)`, `var(--brand-color-accent-soft)`). Validate MIME against an explicit allowlist plus an extension fallback (browsers vary — macOS sometimes labels CSVs as `application/vnd.ms-excel`). Reject wrong types with an inline notice, not an exception. Drop should route through the **same** ingest path as the toolbar file `<input>` so behavior stays uniform.

`ToolWorkbench.vue`'s `source-title` and `preview-title` props default to empty and only render when set. Omit them when the pane's identity is already obvious from its content (a source textarea is a source pane, a rendered diagram is a preview pane). Pass them only when there is a real disambiguation need (e.g., a file name or active diagram label).

Workspace stats (row counts, sync time, character length, connection state) belong as **one** inline muted text line below the toolbar head — not as a 3- or 4-card stat grid. Stat-card chrome (`*-summary-grid`, `*-toolbar-stats`) inflates the toolbar without earning its space. Reserve cards for repeated items (history list rows) or genuinely separate surfaces, not for header decoration.

Empty / loading states inside a tool pane should be a single short muted sentence (e.g., `选择或拖入一个 CSV 文件`, `粘贴 Mermaid 源码以预览`), not a kicker + h2 block. The pane's surrounding context already tells the user where they are.

History / archive lists across tool pages share one pattern: compact ~32px-tall single rows, two columns (`minmax(0, 1fr) auto`), left = timestamp + muted distinguishing meta only, right = a small muted `×` delete affordance. **Do not repeat the timestamp in both the title and the meta line.** Drop tool-name prefixes (`Mermaid 图表 ...`, `CSV ...`, `Drawio ...`) — the page IS the tool. The delete `×` is muted by default (`color: var(--shell-muted)` or equivalent low-emphasis); it brightens to a danger color only on row `:hover` / `:focus-within`. Active row is a subtle background tint + inset accent left-border, not an outer ring. Wrap the list in `max-height: min(60vh, 360px); overflow-y: auto` so a long history does not stretch the toolbar vertically.

Display resource counts (`8 个存档`, `12 行`) next to the section they describe, not on a sibling section. An archive count goes in the history header (`历史 · 8`), not the save header. This is information architecture: labels should sit on the data they label.

**No permanent success confirmations.** Do not render an always-on "已启用账户同步" / "已保存" / "已同步" banner when the success state is the user's default. Permanent success banners are visual noise users learn to ignore. Render the affordance only in the state that needs action (e.g., `AccountSyncPanel` renders nothing when authenticated; it only renders the login prompt when `!authenticated`). Transient feedback (a short toast or a brief inline `保存中...` while a request is in flight) is fine — it disappears when the action completes.

**Active state via solid fill, not stacked rings.** When indicating selection on chip-style buttons (`example chip`, tab, segmented control), use a solid `background: var(--brand-color-accent)` + contrasting text fill. Avoid stacking a `border` + `box-shadow` ring + accent color all on the same active element — the resulting double outline reads as "stuck/disabled" rather than "selected". `:focus-visible` rings layer on top of either state for keyboard users; that single ring is enough.

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

Nuxt UI is the preferred UI library for interactive controls across the app. Register it through the Quasar boot file (`src/boot/nuxt-ui.js`) and import its CSS once from `src/css/nuxt-ui.css`. Use `UButton`, `UInput`, `UTextarea`, `USelect`, `UPopover`, `UDropdownMenu`, `UModal`, `UAlert`, and related Nuxt UI primitives for buttons, links, fields, menus, popovers, and dialogs. For validation-heavy flows, use `UForm` + `UFormField` so field errors live next to their inputs instead of being hand-rendered in page-specific markup.

Nuxt UI runs inside the existing Quasar/Vite shell, not Nuxt. Keep `colorMode: false` in `quasar.config.js`; the project owns system/light/dark switching in `SiteThemeSwitcher.vue` by toggling `html.dark` and storing `xinming-color-mode`. Do not use `UColorModeSelect` or `UApp` unless the app shell is changed and browser-verified again. Shell navigation uses `UButton` links plus `UDropdownMenu`; after changing shell menus, browser-verify the app for Vue recursive render errors before finishing.

Reka UI is not a direct dependency. Do not add direct `reka-ui` imports. Keep direct native controls rare and justified; unavoidable browser primitives such as a hidden file input may be wrapped by a Nuxt UI trigger, and Vue Router's dynamic `<component :is="Component">` in `MainLayout.vue` remains the route outlet rather than a UI control.

**Popover vs Select.** Reach for `USelect` when the dropdown represents a single bound value with no secondary actions per option (e.g., the CSV page-size selector). Reach for `UPopover` when items have per-row secondary actions (delete, archive, edit). The history dropdown on each tool page uses popover semantics because rows have an inline `×` delete, and `@click.stop` on the delete keeps the popover open so users can delete several in a row.

Trigger label for status-style popovers (not value-bound) should describe the current state, not be wired to a `v-model:value` ref. Common pattern: a computed `*TriggerLabel` returning short strings like `历史存档 · N` / `历史 · {timestamp}` / `读取中` / `未登录 · 登录后同步` / `无存档`, plus a `*TriggerDisabled` computed that the trigger's `:disabled` reads. Bind `v-model:open` so the page can close the popover programmatically after a successful action (e.g., `historyOpen.value = false` inside `openArchive`). Place the refresh / list-management affordance inside the popover header, not next to the trigger — the trigger row stays single-line.

> **Gotcha**: Overlay/popover/modal content may be teleported out of the component tree and into `<body>`. `<style scoped>`'s `[data-v-XXX]` attribute selectors do not reliably reach portal-mounted nodes. Put any styling for the portal subtree in an **unscoped** `<style>` block in the same SFC and use page-specific class prefixes (`mermaid-history-popover`, `csv-history-list`, etc.) so the unscoped rules don't leak to other components. Same pattern as MainLayout's `.page-fade-*` route-transition rules. While you are there, set a **solid** `background-color` on both the popover wrapper AND its inner scrollable list — falling back to `transparent` lets the underlying app content bleed through.

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
