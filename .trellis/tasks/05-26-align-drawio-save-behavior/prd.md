# Align Draw.io Save Behavior

## Goal

Make Draw.io and whiteboard save behavior match Mermaid/CSV account archive expectations: the primary `保存` action updates the currently opened archive when one exists, while an explicit `另存为新存档` action creates a new archive snapshot.

## What I already know

- Draw.io and whiteboard share `frontend/src/pages/tools/DrawioEditorPage.vue`.
- Diagram mode uses `useAccountSync('drawio')`; whiteboard mode uses `useAccountSync('drawio-whiteboard')`.
- Current Draw.io `persistSyncedDiagram()` always generates a new archive key, so every save creates a new item.
- Mermaid's `保存` updates `activeItem.item_key` when present and creates a first archive only when no active item exists; `另存为新存档` forces a new key.
- CSV's UI copy also distinguishes normal save from a new version/archive action.

## Requirements

- Top toolbar primary `保存` keeps its current label and login behavior.
- Add a secondary `另存为新存档` action near the primary save button, consistent with Mermaid.
- `保存` should overwrite/update the currently opened Draw.io/whiteboard archive when `accountSync.activeItem` exists.
- `保存` should create a first archive when no active archive exists.
- `另存为新存档` should always create a new archive with a fresh archive key.
- Save dialog defaults should match the mode:
  - overwrite mode: prefill current archive title and remark
  - save-as-new mode: empty title and remark
- Persisted payload should keep XML, xml length, archive key, mode, source marker, and remark.
- Existing draw.io iframe export/save flow should continue to request current XML before persistence.

## Acceptance Criteria

- [ ] Opening an existing Draw.io archive then clicking `保存` updates that same archive item instead of adding a new history row.
- [ ] Opening an existing whiteboard archive then clicking `保存` updates that same archive item instead of adding a new history row.
- [ ] Clicking `另存为新存档` in either mode adds a new history row.
- [ ] Saving without an active archive creates a new archive.
- [ ] Mermaid/CSV behavior is not changed.
- [ ] Frontend lint/build pass or any blocker is reported.

## Definition of Done

- Frontend implementation updated.
- Project frontend quality commands attempted.
- No backend or schema change unless implementation proves it necessary.

## Out of Scope

- Adding a true backend version table.
- Renaming existing sync APIs.
- Reworking the Draw.io page layout beyond the save controls needed for consistency.

## Technical Notes

- Main file: `frontend/src/pages/tools/DrawioEditorPage.vue`.
- Reference behavior: `frontend/src/pages/tools/MermaidPage.vue` around `persistSyncedSource`, `openSaveDialog`, and save/save-as buttons.
- Backend generic sync is upsert by `(user, tool_key, item_key)`; frontend key choice determines update vs new archive.

## Follow-up Requirement: iframe loading recovery

The user approved adding diagnostics and recovery for intermittent Draw.io/whiteboard loading stalls.

Additional requirements:

- If the embedded draw.io iframe does not send `init` within a clear timeout, show a visible loading issue state.
- The issue state should explain that the editor is taking longer than expected, without claiming a confirmed network outage.
- Provide a `重试加载` action that reloads the iframe and restarts the readiness timer.
- Keep `原始编辑器` available as a fallback path.
- Clear the issue state once the iframe sends `init` and the host loads XML.
- Clean up timers on unmount and mode switches.

Additional diagnosis from user screenshot:

- The page repeatedly reaches the host timeout state, which means the host did not observe a draw.io `init` event.
- Harden the iframe handshake by registering the message listener before mount and accepting object-shaped `postMessage` payloads as well as JSON strings.
