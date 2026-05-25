# demo drawio embed tool

## Goal

Add a small Draw.io/diagrams.net embed demo so the user can see how an iframe-based editor would feel inside the existing Tools workspace.

## What I already know

- The app is a Quasar + Vue 3 frontend with route-level tool pages under `frontend/src/pages/tools/`.
- Existing tool pages use local state and scoped styles, with shared shell classes from `frontend/src/css/app.scss`.
- Tools are listed from `frontend/src/pages/ToolsPage.vue`.
- Routes are configured in `frontend/src/router/routes.js`.
- diagrams.net embed mode uses an iframe and `postMessage` JSON protocol.

## Assumptions

- This is a demo, not a full production diagram storage feature.
- Use the official diagrams.net embed URL first.
- Keep saved diagram data in page memory for the demo; do not add backend tables or sync APIs.
- Keep the page usable without login.

## Requirements

- Add a new Draw.io demo route under Tools.
- Add a Tools page entry for the demo.
- Embed diagrams.net in an iframe using embed/proto JSON mode.
- Send a starter XML diagram after the iframe emits `init`.
- Capture `save`/`autosave` style messages from the iframe and show saved XML status.
- Provide simple controls to reload the saved XML, clear demo state, and open the editor in a new tab if iframe loading is blocked.
- Keep responsive tool-page styling consistent with CSV/Mermaid.

## Acceptance Criteria

- [ ] `/tools/drawio` opens a Draw.io demo page.
- [ ] Tools page links to the demo.
- [ ] The iframe loads diagrams.net embed mode.
- [ ] The page can receive and display saved XML length/time from draw.io messages.
- [ ] Frontend lint passes.
- [ ] Frontend build passes.

## Definition of Done

- Demo is implemented and verified in browser.
- Lint/build are green.
- Trellis task is committed and archived after completion.

## Out of Scope

- Backend persistence.
- Account synchronization.
- Multi-diagram history.
- Self-hosting diagrams.net.
- Full draw.io custom UI/theme control.

## Technical Notes

- Candidate files: `frontend/src/pages/tools/DrawioPage.vue`, `frontend/src/router/routes.js`, `frontend/src/pages/ToolsPage.vue`.
- Relevant specs: `.trellis/spec/frontend/index.md`, `component-guidelines.md`, `quality-guidelines.md`.
