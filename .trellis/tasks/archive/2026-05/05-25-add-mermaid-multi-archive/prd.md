# Add Mermaid Multi Archive

## Goal

Make Mermaid account sync keep multiple cloud archives like Draw.io instead of overwriting one default draft, so users can preserve multiple diagrams or versions.

## What I Already Know

- Mermaid currently uses `useAccountSync('mermaid')` with the default `itemKey`, so save/load/delete target a single `default` item.
- Draw.io now uses the generic sync API as a multi-entry archive by generating a unique `itemKey` per save.
- The generic sync composable already supports `loadItems()`, `saveItem({ nextItemKey })`, and `deleteItem(itemKey)`.
- No backend change should be required.

## Requirements

- Each Mermaid account save creates a new sync item with a unique archive key.
- Saved payload includes the source plus useful metadata such as line count, character count, archive key, and source type.
- The authenticated sidebar shows the list of Mermaid cloud archives.
- Users can refresh the archive list.
- Users can load one archive back into the editor.
- Users can delete one archive without deleting other archives.
- Unauthenticated editing, examples, copy, preview, and SVG download remain usable.
- User-facing copy should describe archives, not a single default draft.

## Acceptance Criteria

- [ ] Mermaid no longer saves to the default item key during normal account sync.
- [ ] Saving twice creates two cloud archive entries.
- [ ] Clicking an archive loads its `payload.source` into the editor.
- [ ] Deleting an archive removes only that archive and clears the active marker if needed.
- [ ] Existing local Mermaid editor, rendering, copy, and download behavior still works.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Out Of Scope

- Renaming archives after save.
- Editing an existing archive in place.
- Backend schema or API changes.
- Migrating existing `default` Mermaid drafts.

## Technical Notes

- Frontend page: `frontend/src/pages/tools/MermaidPage.vue`
- Sync composable: `frontend/src/composables/useAccountSync.js`
- State spec: `.trellis/spec/frontend/state-management.md`
