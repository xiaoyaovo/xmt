# Unify Tool Save Cards

## Goal

Create a shared save card component for CSV, Mermaid, and Draw.io so save/new-save actions use one visual and copy pattern across tool pages.

## What I Already Know

- `ToolArchivePanel.vue` now unifies the cloud archive list/login/empty states.
- Save controls are still page-local:
  - CSV combines file selection and save in a local upload panel.
  - Mermaid combines examples, save, save-as-new, and reset.
  - Draw.io combines stats, export, save, reload, and reset.
- The repeated part is the save card shell: title, status badge, save button, optional save-as/new button, optional secondary actions, helper text, and `AccountSyncPanel`.

## Requirements

- Add a reusable `ToolSavePanel.vue` component under `frontend/src/components/tools/`.
- The component owns:
  - panel shell styling
  - top-line kicker/title/status slot
  - primary save button
  - optional save-as/new button
  - optional secondary actions slot
  - helper copy
  - account sync prompt
- CSV, Mermaid, and Draw.io should use the component for their primary save cards.
- Tool-specific controls remain in slots:
  - CSV file picker
  - Mermaid example buttons
  - Draw.io summary stats and event notices
- Preserve current save behavior for all three tools.
- Keep labels consistent: primary action is "保存" / "登录后保存"; optional extra action is "另存为新存档" where applicable.

## Acceptance Criteria

- [ ] CSV, Mermaid, and Draw.io save areas use `ToolSavePanel.vue`.
- [ ] Existing CSV local preview/save behavior still works.
- [ ] Existing Mermaid save/update and save-as-new behavior still works.
- [ ] Existing Draw.io export/save/reload/reset behavior still works.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Out Of Scope

- Backend API changes.
- Changing Draw.io persistence semantics from snapshot save to overwrite.
- Adding tests beyond existing build/lint/browser smoke checks.
