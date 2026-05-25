# Xinming Backend

Minimal FastAPI backend scaffold for the Xinming project.

## Stack

- FastAPI
- Tortoise ORM
- MySQL
- Pydantic Settings
- Aerich

## Quick start

1. Create and activate the environment:

```bash
uv sync
```

2. Copy environment variables:

```bash
cp .env.example .env
```

3. Start the server:

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

4. Initialize Aerich metadata:

```bash
uv run aerich init -t app.db.config.TORTOISE_ORM
uv run aerich init-db
```

## Routes

- `GET /api/v1/health`

