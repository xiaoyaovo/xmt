# Xinming

Personal site and utility hub monorepo.

## Structure

- `frontend/`: Quasar + Vue 3 frontend, including PWA, Electron, and Capacitor targets
- `backend/`: FastAPI + Tortoise ORM backend

## Frontend

```bash
cd frontend
pnpm dev
```

## Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
