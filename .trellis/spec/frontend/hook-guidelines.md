# Frontend Composable Guidelines

Composables live in `frontend/src/composables/` and use `use*` naming. They encapsulate reusable stateful behavior, not view layout.

## Shape

A composable should:

- Import Vue primitives explicitly.
- Keep internal helper functions near the top.
- Own refs for loading, error, selected item, and derived state.
- Return the refs and actions the caller needs.
- Avoid importing page components or route components.

Reference files:

- `useAccountSync.js`
- `useCsvPreview.js`
- `useBrandTheme.js`

## Async State

For async actions, use the local pattern:

- Set `loading`/`saving`/`deleting` before the request.
- Clear `errorMessage` at the start.
- Catch expected request errors and store `error.message`.
- Reset loading flags in `finally`.
- Return a useful value (`item`, `[]`, `null`, or `false`) so pages can decide how to update UI.

`useAccountSync()` is the canonical example for authenticated server state.

## Auth-Aware Composables

When a composable depends on auth:

- Use `useAuthStore()`.
- Call `auth.refreshMe()` only when `auth.initialized` is false.
- Do not assume an access token means a valid logged-in user.
- For save actions that require login, redirect through `auth.loginWithGitHub()` instead of failing silently.

## Browser Work

Browser-heavy work belongs in a composable when it is independent of layout. `useCsvPreview()` owns Papa Parse parsing and returns a normalized preview object to the page.

When browser APIs may not exist in SSR or tests, guard with `typeof window === 'undefined'` in lower-level helpers. `themeCssVars.js` and `http/index.js` show this pattern.

## Derived Data

Use `computed()` for derived values that the template consumes, such as:

- `rowCount`
- `fileSummary`
- `syncLabel`
- `canSync`

Do not duplicate derived data in independent refs unless there is a concrete caching or async reason.

## Avoid

- Mutating Pinia store internals from several unrelated composables.
- Hiding navigation side effects inside generic utilities; auth-specific login is acceptable in `useAccountSync()` because that composable is explicitly auth-aware.
- Returning raw Axios response wrappers. Lib helpers already unwrap `response.data`.
