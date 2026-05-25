# fix drawio archive save flow

## Goal

Make Draw.io account saving behave as a single clear save action and prevent diagrams.net from keeping the embedded editor in a modified state after the host app has archived the XML.

## What I already know

- The Draw.io page currently saves account drafts by setting `syncAfterNextExport`, sending `export`, then persisting the returned XML.
- User testing shows they first click draw.io's own save and then click the left-side save to avoid reload-site prompts.
- diagrams.net embed mode expects the host app to respond with status information after save/persist actions so the editor knows changes are no longer modified.
- The existing spec already notes that host-initiated XML fetch should use `export`, while `save` is editor-emitted.

## Assumptions

- The host page should handle draw.io's internal save event by persisting the returned XML to the same account draft when logged in.
- The left-side "sync to account" button should export fresh XML and persist it without requiring a prior draw.io save click.
- After successful account persistence, the host page should send a `status` message with `modified: false` to the iframe.
- Logged-out users can still export XML locally; draw.io internal save should not silently persist without login.

## Requirements

- Add a post-save status acknowledgement to draw.io after the host saves XML successfully.
- Handle draw.io `save` events as account-save attempts when the user is authenticated.
- Keep left-side save as one-click export-then-persist.
- Show a clearer transient saving state while waiting for the iframe export response.
- Avoid stale pending-save state when draw.io returns errors.
- Keep unauthenticated local editing/export working.

## Acceptance Criteria

- [ ] One click on the left-side account save exports current iframe XML and saves it to account sync.
- [ ] When draw.io emits a `save` event with XML and the user is authenticated, the host persists it to account sync.
- [ ] After successful persistence, the host sends a draw.io `status` message marking the file unmodified.
- [ ] The save button is disabled and indicates a pending export/save state while waiting.
- [ ] Lint and build pass.

## Definition of Done

- Frontend implementation is complete.
- The protocol lesson is recorded in frontend specs.
- Trellis task is committed and archived.

## Out of Scope

- Multi-file Draw.io history.
- Backend schema changes.
- Self-hosted diagrams.net.
- Auth login popup flow changes.

## Technical Notes

- Relevant file: `frontend/src/pages/tools/DrawioPage.vue`.
- Relevant spec: `.trellis/spec/frontend/component-guidelines.md`.
