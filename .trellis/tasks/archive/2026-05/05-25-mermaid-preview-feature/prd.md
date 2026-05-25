# Mermaid preview feature

## Goal

Implement a usable Mermaid live preview page inspired by the official Mermaid Live Editor: users edit Mermaid source in a code panel and see the rendered diagram update in a preview panel.

## What I Already Know

* The user asked for Mermaid preview and specifically mentioned referencing the official online preview.
* `frontend/src/pages/tools/MermaidPage.vue` is currently only a placeholder.
* Official Mermaid docs describe Live Editor as a `Code` panel plus instant `Preview` panel.
* Official usage docs recommend using the Mermaid npm package and manually rendering via `mermaid.initialize({ startOnLoad: false })` plus `mermaid.render(...)` for app integrations.
* The frontend is a Quasar + Vue 3 app.

## Requirements

* Replace the placeholder Mermaid page with a real editor + preview workspace.
* Use the official `mermaid` package for rendering.
* Render diagrams as the source changes, with syntax/render errors shown in the UI.
* Provide practical actions: reset sample, copy source, download SVG.
* Include example presets for common Mermaid diagrams.
* Keep the UI consistent with the existing tool pages and responsive on mobile.

## Acceptance Criteria

* [ ] `/tools/mermaid` shows a Mermaid source editor and rendered SVG preview.
* [ ] Editing valid Mermaid syntax updates the preview.
* [ ] Invalid syntax shows a readable error without breaking the page.
* [ ] Example presets can replace the editor source.
* [ ] Copy and SVG download actions work when supported by the browser.
* [ ] Frontend lint and build pass.

## Out of Scope

* Mermaid Chart account integration.
* AI diagram generation.
* Persistent edit history.
* Drag-and-drop visual editing.
* PNG/PDF export.

## Technical Notes

* Primary file: `frontend/src/pages/tools/MermaidPage.vue`.
* Expected dependency addition: `mermaid`.
* Official references: Mermaid usage docs, getting started/live editor guide.

## Completion Notes

* `/tools/mermaid` has a Mermaid source editor, live SVG preview, syntax error display, example presets, reset, copy, and SVG download actions.
* Mermaid source is wired to reusable account sync so logged-in users can load/save/delete their synced source.
* Verification: `pnpm lint` passed in `frontend/`; `pnpm build` passed in `frontend/` using Node v24.15.0.
