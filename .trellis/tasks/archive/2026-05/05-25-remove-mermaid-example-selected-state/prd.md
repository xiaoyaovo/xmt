# Remove Mermaid example selected state

## Goal

Remove the selected/active visual state from the Mermaid page's left-side diagram type buttons.

## Requirements

* Keep the example buttons clickable.
* Do not show a selected highlight on the left-side example/type list.
* Keep the current example label and preview stats behavior unchanged.

## Acceptance Criteria

* [x] Mermaid example buttons no longer receive `mermaid-example-item-active`.
* [x] No active-state CSS remains for the example buttons.
* [x] Frontend lint passes.

## Completion Notes

* Removed the dynamic selected-state class from Mermaid example buttons.
* Removed the `.mermaid-example-item-active` CSS rule.
* Verification: `pnpm lint` passed in `frontend/` using Node v24.15.0.

## Technical Notes

* Target file: `frontend/src/pages/tools/MermaidPage.vue`.
