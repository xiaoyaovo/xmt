# Fix CSV Save Card Integration

## Goal

Make the CSV save area visibly match the shared `ToolSavePanel` pattern instead of still reading like the old upload-only card.

## What I Already Know

- CSV already imports and renders `ToolSavePanel`.
- The current CSV save card still passes `kicker="上传"`, `title="添加 CSV 文件"`, and `status="20 MB"`, so the visual language does not match Mermaid/Draw.io save cards.
- The file picker should remain inside the card as tool-specific content.

## Requirements

- CSV save card should use save/archive-oriented title copy.
- Keep the file picker in the shared save card slot.
- Preserve CSV local preview and cloud save behavior.
- Keep file size limit visible, but not as the primary card identity.
- Run lint/build and browser smoke check.

## Acceptance Criteria

- [ ] CSV save card displays as a save card, not an upload card.
- [ ] CSV page still has exactly one `.tool-save-panel`.
- [ ] CSV file picker remains usable inside the save card.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Out Of Scope

- Backend upload behavior changes.
- CSV quota changes.
