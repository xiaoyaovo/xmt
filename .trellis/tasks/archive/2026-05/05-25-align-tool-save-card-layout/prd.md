# Align Tool Save Card Layout

## Goal

Make the save/archive entry card feel consistent across CSV, Mermaid, and Draw.io tools.

## Requirements

- Use the same save card information hierarchy across tools:
  - kicker: `保存`
  - title: `云端存档`
  - right status: current archive/sync state, such as archive count or sync state
- Keep the shared `ToolSavePanel.vue` shell and page-level slots.
- Add compact tool-state summaries inside CSV and Mermaid save cards so they match the Draw.io save card structure.
- Preserve existing save, save-as/new, clear/reset, login, and archive behavior.
- Avoid adding a new component unless the existing shared component cannot support the layout.

## Verification

- Run frontend lint/build.
- Inspect CSV, Mermaid, and Draw.io tool pages in the browser to confirm the save card structure is visually aligned.
