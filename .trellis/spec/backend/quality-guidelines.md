# Backend Quality Guidelines

Backend changes should preserve the current separation between API boundaries, services, schemas, and models.

## Required Patterns

- Use async FastAPI route handlers.
- Keep route handlers thin and delegate business logic to `backend/app/services/`.
- Use `Depends(require_current_user)` for authenticated user-owned resources.
- Scope all user-owned queries by `user`.
- Return Pydantic response models from API routes.
- Keep settings in `backend/app/settings/config.py` with environment variable aliases.
- Use `from app...` imports inside backend code.

## Forbidden Patterns

- Reading `.env` manually outside `Settings`.
- Returning ORM objects directly from route handlers.
- Fetching user-owned data without filtering by user.
- Staging runtime data from `backend/storage/`.
- Adding blocking network or file operations to hot paths without a clear reason. Current GitHub OAuth uses `urllib` in the callback route; do not spread that pattern unless replacing it intentionally.
- Adding debug `print()` calls.

## Review Checklist

- Does each new endpoint have a router prefix and response model?
- Are auth dependencies correct for optional versus required auth?
- Are service functions responsible for domain behavior and cleanup?
- Are errors represented with correct HTTP status codes?
- If a model changed, is there a migration?
- Are uploaded files, caches, and secrets ignored?

## Verification Commands

Run from the repo root or backend directory as shown:

```bash
cd backend
uv run python -m compileall app
```

For model or migration changes, also run the appropriate Aerich workflow against a configured development database before relying on the migration.

## Test Status

There is no backend test suite yet. For risky backend changes, prefer adding focused tests before broad refactors. Until tests exist, combine `compileall`, manual endpoint inspection, and careful service review.
