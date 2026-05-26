# Redesign Frontend Single-Column Narrative Layout

## Goal

Replace the current magazine-style nested-card layout with a Linear/Vercel landing-style **single-column narrative**. Visual atoms (color, font, radius, shadow) keep using the existing `editorial` brand tokens — only structure, information density, and entry rhythm change.

## Why

Current layout has known problems:
- Hero stacks ~10 atomic chunks above the fold (badge + title + description + 2 actions + 3 metric cards + status card + N stack cards).
- Three-level card nesting: `.brand-grid-surface` → `.brand-glass-panel` → `.brand-panel-inset`.
- `SiteFeatureBand` and `SiteContentBand` are visually redundant (both heading + 3-col card grid).
- Visual hierarchy is flat — everything is a card.

## Design Principles

1. **One column.** Max content width ~720px text, ~960px container. No side asides.
2. **Numbered rows over cards.** Use `01 / 02 / 03` + hairline dividers instead of grid cards.
3. **One primary CTA per section.** Kill the secondary CTA proliferation.
4. **Scroll-reveal entry.** Each section fades + slides up in stagger as it enters the viewport.
5. **Keep editorial tokens.** Colors, font families, radii, shadows from `brands.editorial` are not changed. Only structural CSS and component templates change.

## Scope

### 1. Shared narrative primitives (foundation)
- New `NarrativeSection.vue` — single-column section wrapper with consistent vertical rhythm, hairline divider, scroll-reveal.
- New `NumberedRow.vue` — `01 — title — description — →` row used by Index/Tools pages.
- New composable `useScrollReveal.js` — IntersectionObserver-based fade/stagger entry (no extra animation library; CSS + small JS).

### 2. MainLayout header slimming
- Drop `site-shell-status` panel from the bar.
- Tighten to: brand mark + primary nav + theme switcher + auth, all on one ~64px tall bar (down from 78px).
- Keep `SiteThemeSwitcher`, `SiteUserMenu`, mobile nav.

### 3. IndexPage rewrite
- Drop `SiteHeroPanel` aside (status card + stack grid).
- Hero = badge + h1 + one-line description + **one** primary CTA. Metrics removed from hero.
- Replace `SiteFeatureBand` + `SiteContentBand` with one `NumberedRow` list (3 rows: CSV / Mermaid / Drawio).
- Optional bottom narrative section for "About / Stack" — single column, no cards.

### 4. ToolsPage rewrite
- Convert from grid-of-cards to numbered-row list (reuses `NumberedRow`).

### 5. Tool pages outer shell (CsvPage / MermaidPage / DrawioPage)
- **Only the page-level container/header/breadcrumb area** changes — the actual editor/preview workspace inside is NOT redesigned.
- Each tool page gets: a thin top strip (← Tools / title / one action), then the existing workspace.
- Remove redundant page-level hero/banner if present.

### 5b. Tool pages internal clutter sweep (scope extension)
Following the same "simple + elegant" intent, sweep visually irrelevant or duplicated bits **inside** each tool page workspace. CSV preview pane internals (chip row, `表格 / CSV 预览` header, summary stat cards) were initially reserved for the parallel `remove-csv-preview-clutter` task; see §5c — they are now absorbed into this task.

Items to remove / consolidate across CsvPage / MermaidPage / DrawioPage:
- Duplicate `h2 "云端存档"` titles in save + history sections. Keep only the `section-kicker` (保存 / 历史) — drop the redundant h2.
- `toolbar-stats` blocks, `toolbar-status` text, Drawio `stats` array. If a stat genuinely carries reading value (row count, sync time), move it inline as small muted text — do NOT keep stat-card chrome.
- `section-kicker` ornament + decorative copy on workspace panes: `源码 / 预览 / 表格 / 编辑器` kickers, plus phrases like `选择或上传一个 CSV 文件` / `输入 Mermaid 源码` / `等待可渲染的图表源码` / `diagrams.net embed`. Empty-state messaging should be ONE short line or an icon hint, not a kicker + h2 block.
- Mermaid `示例 / 图表类型` standalone section: fold the example picker into the toolbar (keep functionality; remove the dedicated section block).

When in doubt about whether something is "decorative" vs "informational", err on the side of removing chrome but keeping the underlying data inline. The implementer is authorized to make judgment calls.

### 5c. CSV preview as a first-class edit + upload surface (scope extension)
The CSV page currently gates the left source `<textarea>` behind `v-if="activeFile"`, so users with no uploaded file see only an empty-state line. Open up the editor as the primary content-entry surface, with the right pane reflecting parsed state live:

- **Always-on left editor**: the `<textarea>` is visible and editable even when `!activeFile`. Empty state can ship with a short placeholder (`Name,Email`-ish header hint or just a muted "粘贴 CSV 内容 / 拖入文件" line on the textarea itself), not a separate empty-state card.
- **Live preview**: editing the textarea pipes through `useCsvPreview` (or whatever the local-parse path is) and updates the right pane in real time, with reasonable debounce.
- **Drag-to-load**: dropping a `.csv` file on the textarea triggers the same `handleFileInput` path. Drag-over state highlights the drop target.
- **Toolbar upload stays**: the existing `选择 CSV` file input remains in the toolbar — drag-and-drop augments, doesn't replace.
- **Save flow unchanged**: the round-5 dialog still gates persistence; this change is only about entry/editing.

This subsumes the prior parallel task `05-25-remove-csv-preview-clutter`: the chip row, `<h2>CSV 预览</h2>` with kicker `表格`, and `.csv-summary-grid` are now removed as part of this work (no longer off-limits). Keep pagination, the table itself, and the page-size selector.

### 6. Global page transition
- Wrap `<router-view>` in transition with fade + small translateY, ~180ms in / ~120ms out.
- Reuse the same easing as scroll-reveal so the system feels coherent.

## Non-Goals

- Do NOT change the editor/preview internals of CSV, Mermaid, Drawio tools.
- Do NOT replace the brand token system or pick a different brand.
- Do NOT introduce a new animation library (anime.js, motion-one, etc.).
- Do NOT touch `AdminPage`, `AuthCallbackPage`, `ErrorNotFound` beyond what `NarrativeSection` cleanup naturally yields.
- Do NOT migrate to a new styling system — keep `<style scoped>` + brand CSS vars.

## Acceptance Criteria

- [ ] `NarrativeSection`, `NumberedRow`, `useScrollReveal` exist in `src/components/site/` and `src/composables/`.
- [ ] IndexPage hero shows only badge + title + description + 1 CTA. No metrics, no aside, no stack cards.
- [ ] IndexPage uses one `NumberedRow` list instead of `SiteFeatureBand` + `SiteContentBand` (the two old components may be left in place for now or removed if unused — implementer's call).
- [ ] ToolsPage shows a numbered-row list, not a card grid.
- [ ] MainLayout header is ~64px tall, no `site-shell-status` block, single horizontal bar.
- [ ] Each tool page (CSV / Mermaid / Drawio) shows a slim top strip with back link + title; workspace below preserves all behavior.
- [ ] Tool page internal clutter swept per §5b: no duplicate `云端存档` h2, no stat-card chrome in toolbar, no decorative pane kickers, Mermaid example picker folded into toolbar.
- [ ] CSV preview internals swept per §5c: chip row, `<h2>CSV 预览</h2>` + `表格` kicker, and `.csv-summary-grid` removed. Pagination + table + page-size selector preserved.
- [ ] CSV left textarea is always visible + editable (no `v-if="activeFile"` gate). Empty state lives inside the textarea (placeholder), not as a separate card.
- [ ] Editing the textarea updates the right preview in real time (parsed via local Papa parse). Reasonable debounce.
- [ ] Dragging a `.csv` file onto the textarea loads it via the same path as the toolbar file input. Drag-over visual feedback.
- [ ] Route changes animate with fade + small vertical translate.
- [ ] Sections fade + stagger on scroll-into-view; respects `prefers-reduced-motion`.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.
- [ ] No regression: theme switcher, auth login/logout, tool functionality all still work.

## Out-of-Scope Follow-ups (do not include here)

- Redesigning the tool workspaces themselves (CSV editor pane, Mermaid editor, Drawio canvas).
- Migrating to a different brand or building a new one.
- Migrating from hash routing to history routing.
