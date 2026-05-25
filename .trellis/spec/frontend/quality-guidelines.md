# Frontend Quality Guidelines

Frontend changes should preserve the Quasar/Vue architecture, pass lint/build, and keep tool pages ergonomic on desktop and mobile.

## Required Patterns

- Use Vue 3 `<script setup>` for new components.
- Keep route-level orchestration in `src/pages/`.
- Put reusable behavior in `src/composables/`.
- Put backend calls in `src/lib/`.
- Use Pinia only for cross-page state.
- Use existing design tokens and CSS variables for visual consistency.
- Keep unauthenticated tool flows graceful when local work is possible.

## Verification Commands

Run from `frontend/`:

```bash
pnpm lint
pnpm build
```

Use a compatible Node version. The build has been verified with Node `v24.15.0`.

The build can emit chunk-size warnings because Mermaid and diagram dependencies are large. A warning is not a failure, but do not ignore new hard build errors.

## Review Checklist

- Does the route exist in `src/router/routes.js` for new pages?
- Does shared async behavior live in a composable or lib helper?
- Does user-facing async UI have loading, empty, and error states?
- Are login-only actions represented as login prompts instead of broken buttons?
- Are buttons/links semantically correct?
- Are generated folders (`dist/`, `.quasar/`, `node_modules/`) unstaged?
- Does the page remain responsive under mobile breakpoints?

## Lint Expectations

The project uses flat ESLint config with Quasar, Vue essential rules, and Prettier skip-formatting. Current local style includes:

- single quotes
- no semicolons
- explicit imports for Vue APIs in source files unless generated auto-imports are already in use
- `prefer-promise-reject-errors` disabled in ESLint, but normalized request errors should still be objects with `code` and `message`

## Avoid

- Adding a new state library or request library for one feature.
- Directly constructing authenticated API headers in components; use the Axios interceptor.
- Hiding build failures behind generated output.
- Styling a tool page with a completely unrelated palette or layout system.
