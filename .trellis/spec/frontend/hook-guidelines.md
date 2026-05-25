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

## Observer-Based Composables

When a composable wraps `IntersectionObserver`, `ResizeObserver`, `MutationObserver`, or similar long-lived browser objects, follow the `useScrollReveal()` pattern (`frontend/src/composables/useScrollReveal.js`):

- Guard for SSR / missing API with `typeof window === 'undefined'` AND `'IntersectionObserver' in window` (or equivalent). In the missing-API branch, degrade to an immediate / no-op behavior so consumers still see usable state.
- Honor `prefers-reduced-motion: reduce` at **both** layers:
  - JS layer: bypass observation and immediately mark elements as "revealed" (or whatever the success state is) so animations don't sit in their initial hidden state.
  - CSS layer: pair with `@media (prefers-reduced-motion: reduce)` in component styles that zero out the entry transform/opacity transition.
  Doing only one layer leaves a regression — either content stuck invisible (JS-only) or content briefly hidden before fading in (CSS-only).
- Disconnect the observer in `onScopeDispose` (or `onUnmounted`) so navigating away does not leak listeners. Store the observer in a module-local ref rather than re-creating it per element.
- Apply per-element stagger via a CSS custom property the composable sets on the element (`--reveal-delay`) rather than recomputing positions in JS each frame.

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
