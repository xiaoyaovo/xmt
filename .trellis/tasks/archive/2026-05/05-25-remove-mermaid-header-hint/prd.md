# Remove Mermaid header hint

## Goal

Remove the descriptive hint text at the top of the Mermaid preview page.

## Requirements

* Remove only the top header description text under the Mermaid page title.
* Keep the page title, editor, preview, and action feedback messages.

## Acceptance Criteria

* [x] The top `section-text` hint is removed from the Mermaid page header.
* [x] Action messages for sync/copy/download remain available.
* [x] Frontend lint passes.

## Completion Notes

* Removed the Mermaid page header description paragraph.
* Kept action feedback notices for account sync, copy, and download actions.
* Verification: `pnpm lint` passed in `frontend/` using Node v24.15.0.

## Technical Notes

* Target file: `frontend/src/pages/tools/MermaidPage.vue`.
