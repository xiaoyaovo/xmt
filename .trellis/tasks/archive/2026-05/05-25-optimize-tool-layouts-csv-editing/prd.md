# Optimize Tool Layouts And CSV Online Editing

## Goal

Unify CSV, Mermaid, and Draw.io into a more workbench-like layout: a single top toolbar for saving, archive/history, file/example actions, and tool-specific commands; below it, a source/editing area and a preview/rendering area sit side by side. CSV should become editable after loading or selecting data, so users can correct table values online before saving.

## What I Already Know

- The user provided a wireframe with a full-width toolbar on top and two lower panes labeled `源` and `预览`.
- The three tool pages currently use a left sidebar for save/archive and a right main area for editing or previewing.
- `CsvPage.vue`, `MermaidPage.vue`, and `DrawioPage.vue` already share `ToolSavePanel.vue` and `ToolArchivePanel.vue`.
- CSV currently parses a local file into `useCsvPreview()` state and renders a read-only table.
- Mermaid already has a clear source textarea and preview pane.
- Draw.io embeds diagrams.net in an iframe and has a local XML preview in the sidebar.

## Assumptions

- "三个工具栏" means the CSV, Mermaid, and Draw.io tool pages should share the same high-level workbench layout, not just button spacing.
- The top toolbar should keep the existing save/archive behavior but present it horizontally and compactly.
- CSV online editing means editing parsed cell values in the browser. It does not require spreadsheet-level formulas, sorting, cell formatting, or collaborative editing in this task.
- CSV saving should persist the edited table content as a new cloud archive version, not overwrite the original uploaded/archive file.

## Requirements

- Add or adapt shared tool layout primitives so the three pages use:
  - a full-width top toolbar area,
  - a lower two-pane area with source/edit pane and preview pane,
  - responsive stacking on narrow screens.
- Move save/archive/history controls for each tool into the toolbar while preserving:
  - login prompts,
  - refresh/list archive behavior,
  - save and save-as/new actions,
  - delete archive actions,
  - existing error/loading states.
- CSV must support online editing:
  - users can edit visible cell values directly in the table,
  - edited rows update preview stats,
  - edited content can be saved to cloud as a new CSV archive,
  - local file upload still works,
  - cloud archive selection still works.
- CSV should provide a clear source/edit pane:
  - selected file/archive metadata,
  - editable table controls,
  - page controls if pagination remains.
- CSV preview pane should show a read-only preview or summary of the edited CSV output.
- Mermaid should keep source textarea on the left/source side and rendered diagram on the right/preview side.
- Draw.io should keep the iframe editor as the source/edit side and place XML/status preview in the preview side.
- Preserve current third-party draw.io iframe protocol safeguards.

## Acceptance Criteria

- [x] CSV, Mermaid, and Draw.io no longer use a left save/archive sidebar as the primary layout.
- [x] Each tool has a top toolbar visually aligned with the user's wireframe concept.
- [x] Each tool has two lower panes: source/edit and preview.
- [x] CSV cells can be edited in-browser and changes remain visible while paging/navigating within the loaded data.
- [x] Saving a CSV after edits uploads the edited CSV content as a new version/archive.
- [x] CSV local upload, archive open, archive delete, and download still work.
- [x] Mermaid source editing, copy, reset, example loading, saving, archive open/delete, and preview still work.
- [x] Draw.io iframe editing, export/load/reset/open standalone, saving, archive open/delete, and XML preview still work.
- [x] Layout is usable at desktop and mobile widths.
- [x] `pnpm lint` and `pnpm build` pass from `frontend/` using a compatible Node version.

## Completion Notes

- Implemented a shared `ToolWorkbench.vue` layout with top toolbar and two lower panes.
- CSV uses editable parsed rows and always saves edited output as a new CSV archive/version.
- Mermaid and Draw.io now use the same workbench structure with concise toolbar text and no success-message clutter.
- Verified in browser on CSV, Mermaid, and Draw.io pages.
- Verified `pnpm lint` and `PATH=/Users/akko/.nvm/versions/node/v24.15.0/bin:$PATH pnpm build`.

## Definition Of Done

- Vue code follows existing `<script setup>` and project component patterns.
- Shared abstractions are introduced only where they reduce repeated layout code across the three tools.
- No generated build output or screenshots are committed.
- Trellis specs are updated if the shared workbench layout becomes a new convention.

## Out Of Scope

- Formula support, multi-sheet spreadsheets, column type inference, sorting/filtering, or bulk CSV transforms.
- Real-time collaboration.
- Replacing Draw.io with another diagram editor.
- Backend schema redesign beyond what is required to save edited CSV content.

## Technical Notes

- Likely affected files:
  - `frontend/src/pages/tools/CsvPage.vue`
  - `frontend/src/pages/tools/MermaidPage.vue`
  - `frontend/src/pages/tools/DrawioPage.vue`
  - `frontend/src/composables/useCsvPreview.js`
  - shared tool components under `frontend/src/components/tools/`
- Current build requires Node `v24.15.0` or another version satisfying Quasar's Node requirement.
