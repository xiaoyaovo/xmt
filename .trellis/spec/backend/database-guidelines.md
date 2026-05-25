# Backend Database Guidelines

The backend uses Tortoise ORM with MySQL and Aerich migrations.

Reference files:

- ORM config: `backend/app/db/config.py`
- DB init: `backend/app/db/init.py`
- Base model: `backend/app/models/base.py`
- Aerich config: `backend/pyproject.toml`
- Migrations: `backend/migrations/models/`

## Models

All persisted models should inherit from `app.models.base.BaseModel`, which provides:

- `id` as a `BigIntField` primary key
- `created_at` with `auto_now_add=True`
- `updated_at` with `auto_now=True`

Each model should set an explicit table name:

- `User.Meta.table = "users"`
- `CsvFile.Meta.table = "csv_files"`
- `ToolSyncItem.Meta.table = "tool_sync_items"`

Use Tortoise field defaults for JSON columns:

- `fields.JSONField(default=list)` for list-shaped data, as in `CsvFile.columns`
- `fields.JSONField(default=dict)` for object-shaped data, as in `ToolSyncItem.payload`

## Relationships And Ownership

User-owned data must be scoped by the `User` relation in every query that reads, updates, or deletes it.

Examples:

- `get_user_csv_file(user, file_id)` filters by both `id` and `user`.
- `get_tool_sync_item(user, tool_key, item_key)` filters by `user`, `tool_key`, and `item_key`.

Never fetch a user-owned object by id alone and check ownership later.

## Query Patterns

Use Tortoise async query APIs directly in services or simple list routes:

- `Model.get_or_none(...)` for nullable lookups.
- `Model.filter(...).order_by(...)` for lists.
- `Model.update_or_create(...)` for upsert-style writes, as in auth user creation and tool sync.
- `await query.count()` before enforcing count quotas.

Keep query composition readable. `csv_service.cleanup_expired_csv_files()` builds a base query and conditionally adds the user filter; use that style for optional scopes.

## Migrations

Aerich migration files live in `backend/migrations/models/` and should match model changes. The current project keeps hand-readable migration SQL in generated files, including:

- `1_20260522000000_auth_csv.py` for `users` and `csv_files`
- `2_20260525000000_tool_sync.py` for `tool_sync_items`

When changing models:

- Add or update an Aerich migration in the same work.
- Include indexes for common access patterns, such as user plus created/updated time.
- Keep foreign keys cascading when child data has no meaning after the user is removed.

## Runtime File Storage

Uploaded CSV bytes are not stored in the database. `CsvFile.storage_path` points at files under `backend/storage/`, and that directory is ignored by git.

Keep file-backed resources in dedicated models and services when they need quotas, retention, download, or row pagination. Use `ToolSyncItem` only for JSON-shaped tool state.

## Tool Sync Items

Use `tool_sync_items` for authenticated, JSON-shaped per-tool state that does not need a dedicated storage model. The ownership key is:

- `user_id`
- `tool_key`
- `item_key`

That tuple must stay unique. `tool_key` is the module namespace (`mermaid`, `csv`, future tools). `item_key` is stable inside that module (`default`, a document id, or another deterministic key). Store flexible data in `payload` and optional display text in `title`.

Do not use this table for binary or file-backed resources. CSV files keep `csv_files` because they need quotas, file paths, row pagination, and download behavior.

## Time

The database config sets `use_tz = False` and `timezone = "Asia/Shanghai"`. Current model timestamps are naive datetimes. When deriving application times, match the current pattern unless the project explicitly migrates to timezone-aware storage.

## Avoid

- Staging `backend/storage/`, `.env`, `.venv`, or `__pycache__`.
- Using mutable Python defaults outside ORM field defaults.
- Creating a table per preview tool when `ToolSyncItem` can store stable JSON state.
