# optimize tools csv mermaid flow

## Goal

Optimize the Tools entry page and the CSV/Mermaid tool display copy so users can see that both tools are usable workspaces, not placeholders, and understand the shared flow before entering.

## What I already know

- `frontend/src/pages/ToolsPage.vue` still labels Mermaid and CSV as placeholders and links with "查看占位页".
- CSV and Mermaid detail pages are already implemented and routed from `/tools/csv` and `/tools/mermaid`.
- The tool pages use a left-control/right-workspace pattern on desktop and stacked layout on mobile.
- Existing frontend specs prefer dense, utilitarian tool panels and existing design tokens.

## Assumptions

- This should be a focused UI/copy refinement, not a new feature or route restructure.
- The top Mermaid hint previously removed should stay removed.
- The Mermaid example selected state should stay enabled.

## Requirements

- Present CSV and Mermaid as available tools on the Tools page.
- Make the entry flow clearer before users enter a tool.
- Avoid placeholder language for already-working tools.
- Keep wording responsive-friendly by avoiding hardcoded "right side" directions where the layout stacks on mobile.
- Preserve existing route structure and tool behavior.

## Acceptance Criteria

- [ ] Tools page cards for CSV and Mermaid describe real capabilities and use non-placeholder statuses/actions.
- [ ] Tools page includes a concise shared workbench flow using existing visual language.
- [ ] CSV and Mermaid empty states do not rely on "right side" wording.
- [ ] Frontend lint passes.

## Definition of Done

- Frontend changes are scoped to tool entry/display polish.
- Lint is green.
- Changes are committed with task bookkeeping.

## Out of Scope

- Backend changes.
- New sync behavior, CSV parsing behavior, or Mermaid rendering behavior.
- Removing Mermaid active example selection.

## Technical Notes

- Relevant files: `frontend/src/pages/ToolsPage.vue`, `frontend/src/pages/tools/CsvPage.vue`, `frontend/src/pages/tools/MermaidPage.vue`.
- Relevant specs: `.trellis/spec/frontend/index.md`, `component-guidelines.md`, `quality-guidelines.md`.
