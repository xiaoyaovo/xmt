# Frontend Development Guidelines

Frontend code lives under `frontend/` and is a Quasar + Vue 3 application using JavaScript, Pinia, Vue Router, Reka UI, UnoCSS, and project CSS/design tokens.

## Stack

- Vue 3 single-file components with `<script setup>`
- Quasar app-vite
- Pinia for cross-page state
- Vue Router hash mode
- Axios request helpers under `src/lib/`
- Project design tokens in `src/design-system/`

## Guidelines Index

| Guide | Purpose | Status |
|-------|---------|--------|
| [Directory Structure](./directory-structure.md) | Where pages, components, composables, lib modules, stores, and design files belong | Filled |
| [Component Guidelines](./component-guidelines.md) | Vue SFC structure, props/events, styling, accessibility, and UI patterns | Filled |
| [Hook Guidelines](./hook-guidelines.md) | Vue composable patterns, async state, and reusable logic | Filled |
| [State Management](./state-management.md) | Local state, Pinia, server state, auth, and account sync | Filled |
| [Quality Guidelines](./quality-guidelines.md) | Lint/build commands and review checklist | Filled |
| [Type Safety](./type-safety.md) | Current JavaScript typing conventions and runtime validation | Filled |

## Pre-Development Checklist

- Read this index and the specific guide for the files you will edit.
- Use `<script setup>` for new Vue components.
- Search `src/lib/`, `src/composables/`, and `src/stores/` before adding new shared logic.
- Keep tool pages usable without login unless the feature is truly account-only.
- Use existing design tokens and shell classes before adding a new visual language.

## Quality Check

Run from `frontend/`:

```bash
pnpm lint
pnpm build
```

Use a compatible Node version. The current build was verified with Node `v24.15.0`; `@quasar/app-vite` rejects older Node versions such as `v22.16.0`.
