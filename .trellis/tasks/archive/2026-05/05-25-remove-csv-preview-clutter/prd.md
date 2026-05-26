# Remove CSV Preview Clutter

## Goal

Remove the nonessential CSV preview header, status, stat cards, and column chips so the right preview pane focuses on the table.

## Requirements

- CSV right preview pane should not show the extra `表格 / CSV 预览 / 已同步` header.
- CSV right preview pane should not show summary stat cards.
- CSV right preview pane should not show column chips.
- Keep pagination controls and the table preview.
- Keep CSV source editing on the left unchanged.

## Acceptance Criteria

- [ ] The preview pane goes directly to pagination/table content.
- [ ] No summary cards or field chips are rendered in CSV preview.
- [ ] Source editor still updates the table preview.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.
