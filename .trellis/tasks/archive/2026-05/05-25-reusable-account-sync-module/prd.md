# Reusable account sync module

## Goal

Create a reusable logged-in account sync layer that preview tools can share. Mermaid should use the generic sync storage for its source content, and CSV should reuse the same frontend account-sync/login state abstraction while keeping its existing file-history upload API.

## What I Already Know

* CSV already has authenticated file history backed by dedicated upload/storage endpoints.
* Mermaid currently has local-only source and preview state.
* The app already has GitHub login, JWT bearer auth, and an authenticated `require_current_user` dependency.
* A generic JSON sync model can support Mermaid and future tools without creating a custom table per preview.

## Requirements

* Add backend model/API for authenticated per-tool JSON sync items.
* Support list, get, upsert, and delete operations scoped to the current user.
* Use stable keys: `tool_key` identifies a module, `item_key` identifies an item inside the module.
* Store flexible JSON payload and optional title for previews.
* Add frontend API helpers and a reusable `useAccountSync()` composable.
* Wire Mermaid to load/save/delete synced source through the composable.
* Wire CSV to use the shared account-sync/login state abstraction while retaining its file upload/history backend.

## Acceptance Criteria

* [ ] Authenticated users can save Mermaid source and reload it after refresh.
* [ ] Unauthenticated users see a login path instead of a broken sync action.
* [ ] Generic sync API is reusable by future modules.
* [ ] CSV still uploads and reads history as before, but uses the shared account sync helper for login/sync UI state.
* [ ] Lint/build/backend import checks pass or blockers are documented.

## Out of Scope

* Conflict resolution across devices.
* Offline sync queues.
* Sharing between users.
* Replacing CSV file storage with JSON sync.

## Technical Notes

* Backend model: `ToolSyncItem`.
* Backend route prefix: `/sync/items`.
* Frontend files: `src/lib/accountSync.js`, `src/composables/useAccountSync.js`, Mermaid/CSV pages.

## Completion Notes

* Backend generic sync API is implemented at `/api/v1/sync/items` with authenticated list, get, upsert, and delete operations.
* `ToolSyncItem` stores per-user `tool_key` + `item_key` JSON payloads with optional titles.
* Frontend helpers live in `frontend/src/lib/accountSync.js`; reusable state lives in `frontend/src/composables/useAccountSync.js`.
* Mermaid uses generic sync for source content; CSV keeps its file-history backend while reusing the login/sync UI abstraction.
* Verification: `pnpm lint` passed in `frontend/`; `pnpm build` passed in `frontend/` using Node v24.15.0; backend import check passed with `uv run python -m compileall app`.
