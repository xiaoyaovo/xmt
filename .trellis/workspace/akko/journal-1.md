# Journal - akko (Part 1)

> AI development session journal
> Started: 2026-05-25

---



## Session 1: Polish tools CSV Mermaid flow

**Date**: 2026-05-25
**Task**: Polish tools CSV Mermaid flow
**Branch**: `main`

### Summary

Updated the Tools entry page to present CSV and Mermaid as usable tools, clarified their shared workflow, adjusted responsive empty-state copy, and verified lint/build plus browser layouts.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `81546d0` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 2: Add Draw.io embed demo

**Date**: 2026-05-25
**Task**: Add Draw.io embed demo
**Branch**: `main`

### Summary

Added a /tools/drawio demo page using diagrams.net iframe embed mode, wired the Tools entry and route, verified postMessage XML export, and documented iframe protocol notes in frontend specs.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `2a1f7ba` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 3: Add Draw.io account archive

**Date**: 2026-05-25
**Task**: Add Draw.io account archive
**Branch**: `main`

### Summary

Connected the Draw.io page to account sync so logged-in users can save, load, and delete one cloud draft while keeping local iframe export usable without login.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `2de7e61` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 4: Fix Draw.io save flow

**Date**: 2026-05-25
**Task**: Fix Draw.io save flow
**Branch**: `main`

### Summary

Adjusted Draw.io save handling so the left-side account save exports fresh XML, draw.io internal save events can persist for authenticated users, and successful host persistence sends status modified=false back to the iframe.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `14977a2` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 5: Add Draw.io multi archive

**Date**: 2026-05-25
**Task**: Add Draw.io multi archive
**Branch**: `main`

### Summary

Changed Draw.io sync from a single default draft to a multi-entry archive using unique sync item keys, with archive list load/delete controls and local export preserved.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `bb15374` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 6: Add Mermaid multi archive

**Date**: 2026-05-25
**Task**: Add Mermaid multi archive
**Branch**: `main`

### Summary

Changed Mermaid account sync from a single default draft to multi-entry cloud archives using unique sync item keys, with archive list load/delete controls and local preview/export preserved.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `a2843d2` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 7: Fix Mermaid archive save action

**Date**: 2026-05-25
**Task**: Fix Mermaid archive save action
**Branch**: `main`

### Summary

Changed Mermaid's primary archive action to save the currently loaded archive, create a first archive when none is active, and added a separate save-as-new action for multi-archive copies.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `c5c5b52` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 8: Unify tool archive panels

**Date**: 2026-05-25
**Task**: Unify tool archive panels
**Branch**: `main`

### Summary

Added a shared ToolArchivePanel for tool cloud archive login/list/empty states, wired CSV, Mermaid, and Draw.io to it, and unified user-facing copy around save and cloud archives.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `4634364` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 9: Unify tool save cards

**Date**: 2026-05-25
**Task**: Unify tool save cards
**Branch**: `main`

### Summary

Added a shared ToolSavePanel for CSV, Mermaid, and Draw.io save/add-new areas, preserving tool-specific controls through slots while standardizing save labels, helper copy, and account sync prompts.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `5258488` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 10: Align CSV save card copy

**Date**: 2026-05-25
**Task**: Align CSV save card copy
**Branch**: `main`

### Summary

Updated the CSV ToolSavePanel copy so it presents as a save/archive card rather than an upload card, while keeping the file picker and existing save behavior unchanged.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `2b790ec` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 11: Align tool save cards

**Date**: 2026-05-25
**Task**: Align tool save cards
**Branch**: `main`

### Summary

Aligned CSV and Mermaid save panels with Draw.io by standardizing the save-card header, archive status, and summary grid, and documented the shared ToolSavePanel convention.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `3844861` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 12: Unify tool workbench layouts

**Date**: 2026-05-25
**Task**: Unify tool workbench layouts
**Branch**: `main`

### Summary

Unified CSV, Mermaid, and Draw.io into a shared ToolWorkbench layout with top toolbar plus source/preview panes. Added CSV browser-side cell editing and edited-content save-as-new archive flow. Trimmed nonessential instructional copy, preserved necessary error states, documented the ToolWorkbench convention, and verified lint/build plus browser snapshots.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `b95b51f` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 13: Fix Draw.io canvas and CSV text editing

**Date**: 2026-05-25
**Task**: Fix Draw.io canvas and CSV text editing
**Branch**: `main`

### Summary

Removed the visible Draw.io XML preview so the page shows a single canvas/editor under the toolbar, while keeping XML internal for save/export/archive. Made CSV's right-side text area editable and parse changes back into columns/rows so table state, dirty status, stats, and saved output update from text edits. Verified lint/build and browser interactions.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `6e9b87e` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 14: Restore CSV preview as read only

**Date**: 2026-05-25
**Task**: Restore CSV preview as read only
**Branch**: `main`

### Summary

Clarified that the left-edit/right-preview split applies to CSV. Removed the CSV right-side text reverse-editing path, restored the right pane to a read-only CSV preview, and kept left table edits driving preview and save output. Verified lint/build and browser behavior.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `25daca7` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete


## Session 15: Fix CSV source editor preview layout

**Date**: 2026-05-25
**Task**: Fix CSV source editor preview layout
**Branch**: `main`

### Summary

Corrected CSV workbench semantics: the left source pane is now an editable CSV textarea and the right preview pane is a read-only table. Upload/archive data populates the source editor, text edits reparse into table rows, the table no longer contains inputs, and save uses the current source text. Verified lint/build and browser behavior.

### Main Changes

(Add details)

### Git Commits

| Hash | Message |
|------|---------|
| `f635a35` | (see git log) |

### Testing

- [OK] (Add test results)

### Status

[OK] **Completed**

### Next Steps

- None - task complete
