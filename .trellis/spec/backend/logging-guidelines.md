# Backend Logging Guidelines

The backend currently has no project logging abstraction and does not emit application logs from routes or services. Uvicorn/FastAPI server logs provide request/runtime visibility during development.

## Current Posture

Keep backend code quiet by default:

- Do not add `print()` debugging.
- Do not introduce a logging framework for one-off messages.
- Do not log bearer tokens, GitHub OAuth tokens, secrets, uploaded CSV content, or full user profile payloads.

## When To Add Logs

Add explicit logging only when a recurring operational event needs diagnosis and cannot be observed through return values or server logs. Good candidates:

- OAuth provider failures without token values.
- Repeated storage cleanup failures.
- Migration or startup failures if the app adds custom startup checks.

If logging is introduced, centralize configuration under `backend/app/core/` or `backend/app/settings/` instead of configuring loggers inside feature modules.

## Error Visibility

Expected client errors should be represented by `HTTPException` details, not logs. Examples include:

- Missing authentication.
- CSV quota failures.
- Missing user-owned resources.

Unexpected errors should be allowed to propagate so FastAPI/Uvicorn records them during development and the client receives the appropriate server error.

## Avoid

- Logging PII such as email addresses unless there is a documented operational need.
- Logging uploaded file contents or CSV rows.
- Adding noisy success logs for every request.
- Using broad `except Exception as error: print(error)` blocks.
