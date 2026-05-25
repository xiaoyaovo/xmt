# add drawio multi archive

## Goal

Change Draw.io account sync from a single overwritten default draft to a multi-entry archive, similar to CSV history semantics.

## What I already know

- Generic sync storage already supports multiple entries per tool through `item_key`.
- Draw.io currently uses `useAccountSync('drawio')` with default `itemKey = default`, so saves overwrite the same item.
- `useAccountSync.saveItem()` accepts `nextItemKey`, allowing the page to create a new item by passing a unique key.
- CSV history creates a new file record per save; the user wants Draw.io to preserve multiple saved diagrams.

## Assumptions

- Each Draw.io save should create a new archive entry, not overwrite the loaded/current entry.
- Read/opening an archive entry loads it into the iframe but does not switch future saves into overwrite mode.
- The existing generic `/sync/items` API is enough; no backend change is needed.
- Item keys can be client-generated using timestamp plus random suffix.

## Requirements

- Generate a new `itemKey` for every account save.
- Store title, XML, XML length, and created source metadata in each archive payload.
- Show a list of Draw.io archive entries ordered by backend `updated_at` list behavior.
- Allow loading a selected archive entry into the iframe.
- Allow deleting an archive entry.
- Keep unauthenticated local editing/export behavior unchanged.
- Keep successful save status message to draw.io so its unsaved state clears.

## Acceptance Criteria

- [ ] Each click on account save creates a new `drawio` sync item with a unique `item_key`.
- [ ] Existing archive entries appear in the sidebar when logged in.
- [ ] Selecting an archive loads its XML into the editor.
- [ ] Deleting an archive removes that item and refreshes the list.
- [ ] Lint and build pass.

## Definition of Done

- Frontend implementation is complete.
- No backend schema/API changes are required.
- Trellis task is committed and archived.

## Out of Scope

- Renaming archive entries.
- Overwriting a selected archive entry.
- Search/filter for archive entries.
- Server-side pagination or quotas for Draw.io archives.

## Technical Notes

- Relevant files: `frontend/src/pages/tools/DrawioPage.vue`, `frontend/src/composables/useAccountSync.js`, `.trellis/spec/frontend/state-management.md`.
