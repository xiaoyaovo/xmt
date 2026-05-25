# CSV preview feature

## Goal

Implement an immediately usable CSV preview flow in the frontend so users can select a local CSV file and inspect its columns, row count, file size, delimiter, and table data before or without uploading it. Keep the existing authenticated history workflow intact so logged-in users can still persist files and revisit them later.

## What I Already Know

* The user asked to implement "cvs preview"; this task treats that as CSV preview because the repo already has a CSV tool.
* The frontend is a Quasar + Vue 3 app under `frontend/`.
* `frontend/package.json` already includes `papaparse`, so client-side CSV parsing can be implemented without adding dependencies.
* `frontend/src/pages/tools/CsvPage.vue` already has an authenticated CSV history page backed by `frontend/src/lib/csvFiles.js`.
* Backend CSV upload, listing, row pagination, download, and delete endpoints already exist.

## Assumptions

* Local preview should be available without GitHub login.
* Selecting a file should parse it in the browser and show the local preview immediately.
* If the user is logged in, the same selected file should also be uploadable into the existing 30-day history.

## Requirements

* Allow selecting `.csv` / `text/csv` files locally.
* Parse CSV in the browser using the existing `papaparse` dependency.
* Show filename, file size, delimiter, column count, row count, parse warnings, detected columns, and a bounded table preview.
* Keep the existing authenticated upload/history/download/delete behavior.
* Make the unauthenticated state a prompt to log in for history, not a blocker for local preview.
* Handle parse errors with a user-visible message.

## Acceptance Criteria

* [ ] Visiting `/tools/csv` without logging in still allows choosing and previewing a local CSV file.
* [ ] Choosing a valid CSV updates preview metrics and table rows.
* [ ] Logged-in users can save the selected local file to history.
* [ ] Existing history row pagination and delete/download actions continue to work.
* [ ] Lint/build checks pass or any blocker is documented.

## Out of Scope

* Editing CSV data.
* Exporting transformed CSV files.
* Server-side preview endpoint changes.
* Advanced filtering/searching/sorting.

## Technical Notes

* Primary files: `frontend/src/pages/tools/CsvPage.vue`, `frontend/src/composables/useCsvPreview.js`.
* Existing backend source inspected: `backend/app/services/csv_service.py`, `backend/app/api/v1/csv_files.py`.
* Relevant guidance read: Vue best practices, frontend design skill, Trellis frontend index and quality/component/hook specs, code reuse thinking guide.
