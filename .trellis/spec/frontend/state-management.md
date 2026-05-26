# Frontend State Management

The frontend uses Pinia for cross-page application state and local refs/composables for page/tool state.

## State Categories

- Global auth state: `frontend/src/stores/auth.js`
- Tool/page state: local refs in page components
- Reusable tool state: composables in `frontend/src/composables/`
- Server requests: API helpers in `frontend/src/lib/`
- Theme selection: `useBrandTheme()` plus design-system storage helpers

## Pinia

Use Pinia when state must be shared across layout, pages, and components. The current store is `useAuthStore`, which owns:

- persisted access token lookup
- current user
- loading/initialized flags
- unified login-page redirect plus provider redirects
- password-login token acceptance
- logout

Do not create a Pinia store for state that belongs to a single page. CSV selected file, active rows, Mermaid source, and render status stay local to their pages/composables.

## Auth State

`auth.authenticated` means `auth.user` exists after `/auth/me` has confirmed the token. A token in local storage alone is not enough.

Use `auth.initialized` before showing final logged-in/logged-out UI. `useAccountSync()` demonstrates this with `ensureAuth()` and `syncLabel`.

## Server State

Server requests should flow through `src/lib/` helpers:

- `auth.js` wraps auth endpoints and local token storage.
- `auth.js` owns login URL construction: `loginPageUrl()` for the unified page and provider-specific
  OAuth URLs for the backend start endpoints. Components should call Pinia actions or these helpers,
  not hardcode `/auth/<provider>/login` URLs.
- `csvFiles.js` wraps upload/history/rows/download/delete.
- `accountSync.js` wraps generic sync endpoints.

Components and composables should catch the normalized error object from `src/lib/http/interceptors.js`, which has `code`, `message`, and `error`.

## Account Sync

Use `useAccountSync(toolKey, { itemKey })` for logged-in account synchronization shared by tool pages.

- `toolKey` must match the backend `/sync/items/{tool_key}` namespace.
- `itemKey` defaults to `default` and should be stable for the synced document.
- Call `loadItem()` to hydrate local tool state after auth initialization.
- Call `saveItem({ title, payload })` to persist JSON-shaped state.
- If the tool owns files or binary data, keep its domain-specific API and use `useAccountSync()` only for login/sync UI state.

Mermaid and Draw.io use generic sync as multi-entry archives. Mermaid's primary save updates the currently loaded archive item and creates a first archive when none is loaded; its save-as action generates a unique `itemKey` for a new source archive. Draw.io generates a unique `itemKey` for each saved XML because its embedded editor save flow behaves like exporting a new diagram snapshot. CSV keeps `csvFiles.js` for file history because the backend owns upload quotas, storage paths, and row pagination.

## URL State

The app currently uses Vue Router hash mode and does not encode tool state in query params. Do not add URL state casually; use it only when reload/share behavior is part of the feature.

## Avoid

- Putting transient form/input state into Pinia.
- Reading or writing `localStorage` from arbitrary components when `auth.js` or design-system helpers already own the key.
- Duplicating server state in multiple stores and composables without a clear source of truth.
