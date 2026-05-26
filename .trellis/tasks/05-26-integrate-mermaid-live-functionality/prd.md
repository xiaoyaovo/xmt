# Integrate Full Mermaid Live Functionality

## Context

The current Mermaid tool already supports editing source, live preview, example snippets, SVG download, and account sync archives. The user wants it upgraded into a more complete Mermaid Live-style workbench while keeping it integrated in the existing Vue/Quasar app rather than deploying the upstream Svelte app as a separate Docker service.

Official Mermaid Live Editor describes its core feature set as editing and previewing Mermaid charts in real time, saving the result as SVG, and generating shareable viewer/editor links.

## Goals

- Keep the Mermaid page usable without login.
- Add shareable editor/viewer links encoded into the local route.
- Hydrate the editor from a shared URL on page load.
- Add export/copy actions beyond the existing SVG download: copy SVG, copy Markdown, download PNG, and open a read-only viewer link.
- Add Mermaid rendering settings in the toolbar: theme, security level, flowchart curve, and font family.
- Persist Mermaid settings with account sync archives.
- Add more diagram templates so common Mermaid diagram types are available quickly.
- Add preview controls for zoom/reset and responsive scrolling.
- Preserve current save semantics: primary save updates the active archive; save-as creates a new archive.

## Non-Goals

- Do not embed the upstream Mermaid Live Editor Svelte application.
- Do not introduce a separate Mermaid Docker service for this feature.
- Do not add a backend renderer in this iteration; client-side Mermaid rendering remains the source of truth.

## Acceptance Criteria

- The Mermaid tool still renders the existing default diagram.
- Editing source or changing render settings re-renders the preview.
- Shared links can be copied and opened to restore source and settings.
- Viewer links open the same page in read-only preview mode.
- SVG and PNG downloads produce usable files when the diagram renders successfully.
- Archives store and restore source plus render settings.
- `pnpm lint` and `pnpm build` pass from `frontend/`.
