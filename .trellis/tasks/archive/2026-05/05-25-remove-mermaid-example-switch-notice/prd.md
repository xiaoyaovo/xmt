# Remove Mermaid example switch notice

## Goal

Remove the notice shown above the Mermaid editor when switching example diagram types.

## Requirements

* Clicking a Mermaid example should still replace the editor source.
* Do not show `已切换到...示例。` after switching examples.
* Keep other action feedback messages, such as reset, sync, copy, and download.

## Acceptance Criteria

* [x] `useExample()` no longer writes an action message.
* [x] Other `actionMessage` behaviors remain unchanged.
* [x] Frontend lint passes.

## Completion Notes

* Removed the `actionMessage` assignment from `useExample()`.
* Kept reset, sync, copy, and SVG download feedback messages.
* Verification: `pnpm lint` passed in `frontend/` using Node v24.15.0.

## Technical Notes

* Target file: `frontend/src/pages/tools/MermaidPage.vue`.
