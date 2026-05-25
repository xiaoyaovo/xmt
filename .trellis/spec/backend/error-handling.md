# Backend Error Handling

Backend errors are returned through FastAPI's normal `HTTPException` path. There is no custom global error envelope today.

## API Boundary

Use `HTTPException` with a precise status code and a short `detail` message for expected client-facing failures.

Examples:

- `require_current_user()` returns `401 Authentication required` when no valid bearer token exists.
- CSV upload rejects non-`.csv` files with `400`.
- CSV upload rejects files over the configured size with `413`.
- User-owned CSV and sync lookups return `404` when the record is missing or inaccessible.
- GitHub OAuth misconfiguration returns `500`.

## Authentication

Authentication is split into optional and required dependencies:

- `get_current_user()` returns `User | None` and never raises for missing or invalid bearer tokens.
- `require_current_user()` wraps it and raises a `401` when authentication is mandatory.

Use the optional dependency for endpoints like `/auth/me`; use the required dependency for user-owned resources like CSV history and sync items.

## Service Errors

Services may raise `HTTPException` for domain failures that are already part of the HTTP contract:

- Quota and file type checks in `csv_service.py`.
- Missing user-owned resources in `get_user_csv_file()` and `get_tool_sync_item()`.

Keep unexpected exceptions unhandled unless cleanup is required. `save_upload_file()` catches broad exceptions only to delete a partially written upload, then re-raises.

## Cleanup

If a function creates external side effects before all validation finishes, it must clean up on failure.

Reference pattern:

- `save_upload_file()` writes the upload to disk, validates quota and CSV shape, deletes the target path on any exception, and always closes the upload.

Deletion cleanup should be best-effort when the database operation is the source of truth. `delete_storage_file()` ignores `OSError` if removing the stored file fails.

## Client Messages

The backend currently returns a mix of English auth/config messages and Chinese user-facing CSV messages. When adding feature-specific user-facing errors, match the surrounding route or service. Shared infrastructure messages can stay English.

## Avoid

- Returning raw exception strings from unexpected errors.
- Exposing secrets or raw OAuth provider responses in `detail`.
- Treating an invalid/missing optional token as a server error.
- Swallowing exceptions after partial writes without either cleanup or a clear fallback.
