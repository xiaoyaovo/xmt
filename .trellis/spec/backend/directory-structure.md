# Backend Directory Structure

The backend is rooted at `backend/`. Runtime application code is inside `backend/app/`; generated or deployment-adjacent files stay outside it.

## Layout

```text
backend/
  app/
    api/              FastAPI routers and dependencies
      v1/             Versioned route modules
    core/             FastAPI middleware and app-level helpers
    db/               Tortoise configuration and initialization
    models/           Tortoise ORM models
    schemas/          Pydantic request/response schemas
    services/         Business logic and side effects
    settings/         Pydantic settings
    main.py           FastAPI app factory
  migrations/         Aerich migration files
  storage/            Runtime uploaded files, ignored by git
  main.py             Uvicorn entrypoint shim
```

Reference files:

- `backend/app/main.py` creates the app, registers middleware, and mounts `api_router` under `/api`.
- `backend/app/api/__init__.py` mounts the v1 router under `/v1`.
- `backend/app/api/v1/__init__.py` collects feature routers and tags.

## Feature Organization

Use the existing four-part feature shape when adding backend functionality:

- API boundary in `backend/app/api/v1/<feature>.py`
- Domain behavior in `backend/app/services/<feature>_service.py`
- Request/response models in `backend/app/schemas/<feature>.py`
- Database state in `backend/app/models/<feature>.py`

Examples:

- CSV history: `api/v1/csv_files.py`, `services/csv_service.py`, `schemas/csv_file.py`, `models/csv_file.py`
- Generic sync: `api/v1/tool_sync.py`, `services/tool_sync_service.py`, `schemas/tool_sync.py`, `models/tool_sync_item.py`
- Auth: `api/v1/auth.py`, `services/jwt_service.py`, `schemas/auth.py`, `models/user.py`

## Route Modules

Route modules should be thin. They should:

- Define `router = APIRouter(prefix="...")`.
- Use `Depends(require_current_user)` for authenticated endpoints.
- Call a service for business logic.
- Serialize ORM objects through a small local `serialize_*` function or Pydantic schema.
- Return explicit response models for JSON endpoints.

Do not put file parsing, quotas, token signing, or multi-step persistence directly in route handlers. `csv_files.py` delegates those responsibilities to `csv_service.py`; follow that pattern.

## Services

Services own side effects and domain decisions:

- File storage and cleanup live in `csv_service.py`.
- JWT signing and decoding live in `jwt_service.py`.
- Generic account sync persistence lives in `tool_sync_service.py`.

Services may raise `fastapi.HTTPException` when the error is part of the API contract, such as quota failures or missing user-owned resources.

## Naming

- Route files use plural resource names when the API is resource-oriented, such as `csv_files.py`.
- Service files end with `_service.py`.
- Schema files use the resource name, such as `csv_file.py` or `tool_sync.py`.
- ORM model class names are singular PascalCase and table names are explicit snake_case via `class Meta`.

## Avoid

- Creating controllers for new work unless the project starts using `backend/app/controllers/`; it is currently empty.
- Importing route modules from services.
- Adding feature logic to `backend/main.py`; it is only an entrypoint shim.
