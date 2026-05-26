# Fix CSV files title column error

## Goal

Fix the backend 500 on `GET /api/v1/csv/files` caused by the running MySQL schema missing the `csv_files.title` column while the Tortoise `CsvFile` model expects `title` and `remark`.

## What I already know

- The failing endpoint is `GET /api/v1/csv/files`.
- The traceback fails in Tortoise/MySQL with `Unknown column 'title' in 'field list'`.
- `backend/app/models/csv_file.py` defines nullable `title` and `remark` fields.
- `backend/app/api/v1/csv_files.py` serializes `title` and `remark` in CSV history responses.
- `backend/migrations/models/3_20260525120000_csv_title_remark.py` already adds `title` and `remark` to `csv_files`.
- `uv run aerich heads` currently fails before checking DB state with `Old format of migration file detected, run aerich fix-migrations`.

## Assumptions

- The intended API behavior is to keep the new `title` and `remark` fields.
- The local database is behind the model/migration state rather than the backend code being wrong.

## Requirements

- Ensure the database can be upgraded so `csv_files.title` and `csv_files.remark` exist.
- Preserve the existing CSV API response shape.
- Avoid unrelated frontend or task-directory changes already present in the worktree.

## Acceptance Criteria

- [ ] Aerich can inspect or apply pending migrations without the old-format migration error.
- [ ] The local database has `csv_files.title` and `csv_files.remark`.
- [ ] `GET /api/v1/csv/files` no longer fails due to missing `title`.
- [ ] Backend code compiles.

## Definition of Done

- Backend compile check run.
- Migration/schema state verified or exact command and blocker recorded.
- No unrelated user changes reverted.

## Out of Scope

- Changing CSV history product behavior.
- Refactoring CSV upload/list logic.
- Reworking the full Aerich migration snapshot strategy beyond what is needed for this fix.

## Technical Notes

- Relevant spec: `.trellis/spec/backend/database-guidelines.md`.
- The backend database guide notes that hand-written migrations can drift from Aerich `MODELS_STATE`.
- Relevant files: `backend/app/models/csv_file.py`, `backend/app/api/v1/csv_files.py`, `backend/migrations/models/3_20260525120000_csv_title_remark.py`.
