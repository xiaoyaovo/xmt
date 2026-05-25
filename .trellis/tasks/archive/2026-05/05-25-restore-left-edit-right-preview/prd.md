# Restore CSV Left Edit Right Preview

## Goal

Restore the CSV tool interaction model so the left pane is the editable area and the right pane is a read-only preview. Draw.io should remain focused on the canvas/editor and must not expose XML editing to normal users.

## What I Already Know

- The user clarified that "left edit, right preview" applies to CSV.
- The previous change made CSV's right-side CSV text textarea editable, which conflicts with the intended source/edit and preview split.
- Draw.io XML is too complex for normal users to edit directly, so the UI should not expose XML editing.

## Requirements

- CSV left pane keeps the editable table.
- CSV right pane becomes read-only preview again.
- Editing CSV cells on the left still updates the right preview text.
- Saving CSV still uses the edited table content.
- Do not reintroduce Draw.io XML editing.

## Acceptance Criteria

- [x] CSV right-side textarea is read-only.
- [x] CSV right-side textarea does not parse user text input back into rows.
- [x] CSV left table cell editing still updates the right preview.
- [x] CSV edited content still saves as a new version/archive.
- [x] Draw.io UI still does not expose XML editing.
- [x] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Completion Notes

- Removed the CSV right-side text editing handler and composable parser.
- Restored the right pane as a read-only CSV text preview.
- Browser-verified: editing the left table updates the read-only preview text.

## Definition Of Done

- Keep the fix scoped to CSV behavior unless a cleanup is required.
- Browser-check CSV after implementation.
