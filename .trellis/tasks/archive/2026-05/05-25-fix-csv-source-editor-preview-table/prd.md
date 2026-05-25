# Fix CSV Source Editor And Table Preview

## Goal

Make the CSV tool match the intended source/preview model: the left pane is an editable CSV text input, and the right pane is a table preview generated from that text.

## What I Already Know

- The user clarified that "left edit, right preview" means:
  - left: CSV text editor/input box,
  - right: table preview.
- The current CSV page has this reversed: left is an editable table and right is a read-only CSV text preview.
- `useCsvPreview()` already owns Papa Parse parsing and CSV serialization.
- Save should persist the edited CSV text as a new CSV archive/version.

## Requirements

- CSV left pane must be a textarea/editor for CSV text.
- CSV right pane must be a table preview.
- Uploading or opening a cloud archive should populate the left CSV editor.
- Editing CSV text should parse into columns/rows and update the right table preview.
- The right table preview must not be the editing surface.
- Save should upload the current CSV text as a new version/archive.
- Draw.io must not be changed for this task.

## Acceptance Criteria

- [x] CSV source pane contains an editable textarea.
- [x] CSV preview pane contains a table.
- [x] Editing text on the left updates the table on the right.
- [x] The table cells are not editable inputs.
- [x] Saving uses the current text/editor contents.
- [x] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Completion Notes

- Reoriented CSV to source/editor on the left and table preview on the right.
- The CSV textarea now owns the editable source text; table cells are plain text.
- Uploading a CSV populates the editor, editing the editor reparses into the preview table, and save uses the current editor text.
- Browser-verified source edit to `Alice,99` updates the right preview table with no console errors.

## Definition Of Done

- Browser-check CSV upload, text edit, table preview, and readonly table cells.
- Keep changes scoped to CSV and CSV preview composable.
