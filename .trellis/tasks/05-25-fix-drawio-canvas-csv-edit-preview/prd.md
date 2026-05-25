# Fix Draw.io Canvas And CSV Editable Preview

## Goal

Make Draw.io show only the drawing canvas in the workbench and make the CSV right-side CSV text area editable so edits there update the table data and saved CSV output.

## What I Already Know

- The current Draw.io page places the iframe editor in the source pane and raw XML in the preview pane.
- The current CSV page has an editable table in the source pane, but the right-side CSV textarea is read-only.
- `useCsvPreview()` owns parsed CSV rows and can already serialize the current rows with `toCsvText()`.
- Tool pages use `ToolWorkbench.vue` for the toolbar plus source/preview panes.

## Requirements

- Draw.io should not show XML in the page UI.
- Draw.io should show only the canvas/editor area below the toolbar.
- Draw.io save/export/archive behavior must continue using XML internally.
- CSV right-side CSV text area must be editable.
- Editing the right-side CSV text must update parsed columns/rows, table view, dirty state, stats, and saved output.
- Existing CSV cell editing must continue to work.

## Acceptance Criteria

- [x] Draw.io page no longer renders a visible XML textarea.
- [x] Draw.io canvas/editor remains visible and usable.
- [x] CSV right-side textarea is editable.
- [x] Editing CSV text updates the left table and save payload.
- [x] CSV local upload, cloud archive open, and save-as-new still work.
- [x] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Completion Notes

- Draw.io now renders a single canvas/editor pane under the toolbar; XML remains internal state for save/export/archive.
- CSV text edits parse back into columns/rows, reset pagination, update stats, and mark the file dirty.
- Verified in browser: Draw.io has no XML textarea, and CSV right-side text edits update the left table.

## Definition Of Done

- Keep changes scoped to the tool pages/composable.
- No generated build output or screenshots committed.
- Browser-check Draw.io and CSV pages after implementation.
