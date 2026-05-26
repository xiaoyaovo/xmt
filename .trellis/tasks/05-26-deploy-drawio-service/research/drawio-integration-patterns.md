# draw.io Integration Pattern Research

## Question

How should Xinming customize draw.io save/history behavior while keeping draw.io maintainable and usable on desktop, tablet, and phone?

## Findings

Comparable projects mostly treat diagrams.net/draw.io as an editor engine rather than a product UI to fork deeply:

- `marcveens/react-drawio` wraps draw.io in an iframe and exposes host callbacks such as load/save/export.
- GitLab's diagrams.net integration uses iframe + `postMessage`, with the host application owning upload/update/insert behavior.
- `hediet/vscode-drawio` packages draw.io for VS Code, but VS Code owns file persistence and editor lifecycle.
- `jgraph/drawio-nextcloud` integrates draw.io with a host storage system; the host platform owns files and permissions.
- The official `jgraph/drawio` repository can be forked, but that makes Xinming responsible for keeping a custom draw.io distribution current.

## Common Pattern

The stable customization seam is:

1. Load self-hosted draw.io in iframe embed mode with `embed=1&proto=json`.
2. Wait for draw.io's `init` event.
3. Send `{ action: "load", xml }` from the host page.
4. Listen for `save`, `autosave`, and `export` events.
5. Persist XML in the host application's storage.
6. Send `{ action: "status", modified: false }` after successful persistence.

## Recommendation

Use a Xinming-owned fullscreen wrapper page around the self-hosted draw.io iframe.

This keeps:

- draw.io upgrades simple because the Docker image can still be updated independently.
- Xinming save/history/auth behavior in the existing frontend/backend stack.
- mobile/tablet behavior controllable by the wrapper page (`100dvh`, no outer scroll, safe-area padding, fixed toolbar).

Forking draw.io source should be reserved for later if Xinming needs deep native-menu customization that cannot be expressed through embed mode.

## Repo Fit

The current repo already has:

- `frontend/src/pages/tools/DrawioPage.vue` with iframe `postMessage` save/history behavior.
- `frontend/src/composables/useAccountSync.js` and `frontend/src/lib/accountSync.js` for generic per-tool cloud sync.
- `frontend/src/router/routes.js` for tool routes.
- Existing tool entry patterns in `ToolsPage.vue` and `siteHome.js`.

So the lowest-risk implementation is to split the current combined draw.io page into:

- an entry/planning page at `/tools/drawio`
- a fullscreen editor page at `/tools/drawio/editor`
- a history page or history panel backed by the same `drawio` sync key
