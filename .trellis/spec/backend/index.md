# Backend Development Guidelines

Backend code lives under `backend/` and is a FastAPI application with Tortoise ORM, Aerich migrations, Pydantic schemas, and service modules for business logic.

## Stack

- Python 3.11+
- FastAPI async route handlers
- Tortoise ORM with MySQL through `aiomysql`
- Aerich migrations in `backend/migrations/`
- Pydantic Settings in `backend/app/settings/config.py`

## Guidelines Index

| Guide | Purpose | Status |
|-------|---------|--------|
| [Directory Structure](./directory-structure.md) | Where API, service, schema, model, settings, and DB code belongs | Filled |
| [Database Guidelines](./database-guidelines.md) | Tortoise model, query, migration, storage, and naming conventions | Filled |
| [Error Handling](./error-handling.md) | HTTP errors, auth failures, cleanup behavior, and client-facing messages | Filled |
| [Quality Guidelines](./quality-guidelines.md) | Review checklist and verification commands | Filled |
| [Logging Guidelines](./logging-guidelines.md) | Current logging posture and when to add logs | Filled |

## Pre-Development Checklist

- Read this index and the specific guide for the layer you are changing.
- For new or changed endpoints, read `directory-structure.md`, `error-handling.md`, and `quality-guidelines.md`.
- For models, migrations, or stored files, read `database-guidelines.md`.
- Search for an existing route/service/schema pattern before creating a new shape.
- Keep route handlers thin: validation and HTTP boundary concerns in `app/api/v1/`, domain behavior in `app/services/`.

## Quality Check

- Run `cd backend && uv run python -m compileall app` after backend changes.
- If model fields changed, verify the matching Aerich migration under `backend/migrations/models/`.
- Check imports from the repo root package style: `from app...`, not relative parent imports.
- Confirm no secrets, uploaded files, `.env`, virtualenv files, or `__pycache__` are staged.
