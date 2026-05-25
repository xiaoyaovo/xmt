# Fix Mermaid Save Archive Action

## Goal

Fix Mermaid archive actions so the primary button is a real save action, not only an "add new" action. Multi-archive behavior should remain available through an explicit "save as new archive" action.

## What I Already Know

- The current Mermaid page creates a new archive for every account sync.
- User feedback: "有新增，但是没有保存" means the UI lacks an update/save action for the currently loaded archive.
- `useAccountSync.saveItem()` can overwrite an existing sync item when called with the existing `itemKey`.
- Mermaid already tracks `accountSync.activeItem` when an archive is opened.

## Requirements

- Primary Mermaid account action should be labeled as save.
- If an archive is currently active, save should overwrite that archive's item key.
- If no archive is active, save should create a new archive.
- A separate action should allow saving the current source as a new archive copy.
- Success messages should distinguish saved current archive vs saved as new archive.
- The archive list should remain loadable, refreshable, and deletable.

## Acceptance Criteria

- [ ] Loading an archive then clicking save updates that archive instead of creating a new list item.
- [ ] Clicking save without an active archive creates a new archive.
- [ ] Clicking save as new archive always creates a new archive.
- [ ] Button labels and helper copy make the difference clear.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Out Of Scope

- Backend API changes.
- Archive rename UI.
- Migrating existing default Mermaid drafts.
