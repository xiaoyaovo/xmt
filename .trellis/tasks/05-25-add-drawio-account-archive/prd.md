# add drawio account archive

## Goal

Connect the Draw.io demo page to the existing logged-in account sync system so users can save, load, and delete one Draw.io draft tied to their GitHub account.

## What I already know

- `DrawioPage.vue` currently stores exported XML only in page memory.
- `MermaidPage.vue` already uses `useAccountSync('mermaid')` for one account draft.
- `useAccountSync(toolKey, { itemKey })` supports `loadItem`, `saveItem`, and `deleteItem` through `/sync/items/{tool_key}/{item_key}`.
- Draw.io iframe XML is available after sending `{ action: 'export', format: 'xml' }` and handling the returned `export` event.
- The page should remain usable without login; login is only needed for account archive.

## Assumptions

- First version stores a single Draw.io draft under `toolKey = drawio`, `itemKey = default`.
- Store XML in JSON payload as text, not as a file upload.
- Do not add backend schema or API changes because generic sync already exists.
- Preserve demo iframe behavior and route.

## Requirements

- Load the logged-in account draft on page mount when available.
- Save the latest exported Draw.io XML to the account draft.
- Delete the account draft and reset to the starter diagram.
- Show account sync state, errors, and unauthenticated login prompt in the sidebar.
- Keep local export/reload controls usable without login.
- Ensure saving first requests fresh XML from the iframe when the editor is ready, then persists the returned XML.

## Acceptance Criteria

- [ ] Logged-in users can save the current Draw.io XML to account sync.
- [ ] Logged-in users can load the saved Draw.io XML back into the editor.
- [ ] Logged-in users can delete the saved draft and return to the starter diagram.
- [ ] Logged-out users see a login/sync prompt and can still use the local iframe editor.
- [ ] Existing Draw.io iframe export behavior still works.
- [ ] Frontend lint and build pass.

## Definition of Done

- Frontend implementation is complete and verified.
- No backend changes are required.
- Trellis task is committed and archived.

## Out of Scope

- Multi-document Draw.io history.
- File upload/download endpoints.
- Self-hosted diagrams.net.
- Realtime collaborative editing.

## Technical Notes

- Relevant files: `frontend/src/pages/tools/DrawioPage.vue`, `frontend/src/components/tools/AccountSyncPanel.vue`, `frontend/src/composables/useAccountSync.js`.
- Relevant specs: `.trellis/spec/frontend/index.md`, `component-guidelines.md`, `state-management.md`, `quality-guidelines.md`.
