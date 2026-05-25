# Fix Mermaid sync CORS error

## Goal

Fix the Mermaid preview account-sync request so opening `/tools/mermaid` from the frontend dev server does not fail with a browser CORS error when it calls `http://localhost:8000/api/v1/sync/items/mermaid/default`.

## What I Already Know

* The browser reports: `No 'Access-Control-Allow-Origin' header is present on the requested resource`.
* Frontend origin is `http://localhost:9002`.
* Backend default and local env include `http://localhost:9002` in `CORS_ORIGINS`.
* CORS middleware is configured in `backend/app/core/middlewares.py`.
* Mermaid loads synced source on mount through `useAccountSync('mermaid')`.

## Assumptions

* This is a backend response/middleware behavior issue, not a frontend URL typo.
* The fix should preserve authenticated sync requirements while ensuring dev CORS headers are returned for expected origins.

## Requirements

* Reproduce or inspect the sync endpoint behavior with an `Origin: http://localhost:9002` request.
* Ensure CORS headers are returned for configured frontend origins, including error responses.
* Keep `allow_credentials=True` and avoid wildcard origins.
* Avoid weakening auth: unauthenticated sync requests should still return an auth failure, just with CORS headers.

## Acceptance Criteria

* [x] A request to `/api/v1/sync/items/mermaid/default` from origin `http://localhost:9002` includes `Access-Control-Allow-Origin: http://localhost:9002`.
* [x] Opening Mermaid preview no longer surfaces the browser CORS policy error.
* [x] Unauthenticated sync requests still fail as unauthenticated instead of silently succeeding.
* [x] Backend import check passes.

## Technical Notes

* Likely files: `backend/app/main.py`, `backend/app/core/middlewares.py`, `backend/app/settings/config.py`, `frontend/src/composables/useAccountSync.js`.
* Relevant specs: backend directory structure, error handling, and quality guidelines.

## Completion Notes

* Root cause: authenticated sync requests reached MySQL and failed with `Table 'xinming.tool_sync_items' doesn't exist`; the resulting 500 response was emitted outside the existing CORS middleware response path, so the browser reported it as a CORS failure.
* Code fix: wrap the FastAPI app with `CORSMiddleware` as the outer ASGI app in `backend/app/main.py` via `apply_middlewares()` so error responses also include configured CORS headers.
* Local data fix: created the missing `tool_sync_items` table in the local `xinming` database using the existing migration SQL from `backend/migrations/models/2_20260525000000_tool_sync.py`.
* Verification:
  * unauthenticated GET with `Origin: http://localhost:9002` returns `401` with `Access-Control-Allow-Origin: http://localhost:9002`.
  * authenticated GET with no saved Mermaid item returns `404` with `Access-Control-Allow-Origin: http://localhost:9002`.
  * preflight `OPTIONS` returns `200` with expected CORS headers.
  * `uv run python -m compileall app` passes.
