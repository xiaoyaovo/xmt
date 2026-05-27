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

> **Gotcha — `MODELS_STATE` snapshot drifts on hand-written migrations.** Aerich's auto-`migrate` command diffs the current models against the `MODELS_STATE` blob baked into the most recent migration file (see `0_20260519174335_init.py` for the format). The hand-written migrations in this project (`2_...`, `3_...`) do NOT update that blob. The next time someone runs `aerich migrate`, the diff will be computed against the stale snapshot from `1_...` and will re-emit columns that have already been added by `2_...` and `3_...`. When you write a new migration, either: (a) keep hand-writing and accept that future auto-`migrate` runs need manual cleanup, or (b) regenerate the `MODELS_STATE` blob by running `aerich init-db` against a clean DB and copying the resulting snapshot. Pick deliberately; mixing styles invisibly causes duplicate-column errors at deploy time.

### Scenario: Repair drifted hand-written migration state

#### 1. Scope / Trigger

- Trigger: A model field exists in code and in a migration file, but runtime MySQL fails with `Unknown column '<field>' in 'field list'`.
- Trigger: `uv run aerich heads` or `uv run aerich history` fails with `Old format of migration file detected` after a hand-written migration was added without `MODELS_STATE`.

#### 2. Signatures

- Command: `cd backend && uv run aerich heads`
- Command: `cd backend && uv run aerich history`
- Command: `cd backend && uv run aerich fix-migrations`
- DB check: `SHOW COLUMNS FROM \`<table>\`;`
- DB state table: `aerich(version, app, content)`

#### 3. Contracts

- Every migration that can be the latest file in `backend/migrations/models/` must expose a valid `MODELS_STATE` string for Aerich 0.6+.
- The `aerich` table must record only migrations whose SQL effects are already present in the database.
- If a migration's SQL was applied manually, record it with `aerich upgrade --fake` only after verifying the schema matches.
- `aerich fix-migrations` only repairs migrations that have matching records in the `aerich` table. If the broken latest migration is still pending, generate and append `MODELS_STATE` before running `aerich upgrade`.

#### 4. Validation & Error Matrix

- `Unknown column` during ORM select -> compare model fields against `SHOW COLUMNS`.
- `Old format of migration file detected` -> latest migration file lacks a valid `MODELS_STATE`.
- `fix-migrations` reports `No matching record ... Skipping` -> the pending migration is not in `aerich`; repair the file, then run `aerich heads` again.
- Pending migration creates a table/index that already exists -> the schema was applied but the `aerich` record is missing; verify schema before faking.
- `aerich heads` returns no rows -> Aerich believes all migration records are current.

#### 5. Good/Base/Bad Cases

- Good: migration file has SQL plus current `MODELS_STATE`; DB columns exist; `aerich heads` prints `No available heads.`
- Base: DB is behind; run `uv run aerich upgrade` and verify columns.
- Bad: DB has schema changes but `aerich` lacks records; direct `upgrade` may fail on duplicate table/index/column.

#### 6. Tests Required

- Run `cd backend && uv run python -m compileall app`.
- Run `cd backend && uv run aerich heads`.
- For field-related fixes, run a Tortoise query against the affected model to ensure ORM select lists no longer fail.

#### 7. Wrong vs Correct

Wrong:

```bash
cd backend
uv run aerich upgrade
```

If earlier hand-written SQL was already applied outside Aerich, this can fail on duplicate schema objects.

Correct:

```bash
cd backend
uv run aerich heads
uv run python - <<'PY'
import asyncio
from tortoise import Tortoise
from app.db.config import TORTOISE_ORM

async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    try:
        print(await conn.execute_query_dict("SHOW COLUMNS FROM `<table>`"))
    finally:
        await Tortoise.close_connections()

asyncio.run(main())
PY
```

Then either run the missing migration normally, or manually add the verified missing schema and use `uv run aerich upgrade --fake` to repair Aerich bookkeeping.

If the pending migration itself is missing `MODELS_STATE`, generate the state from current Tortoise models and validate it before upgrading:

```bash
cd backend
uv run python - <<'PY'
import asyncio
from tortoise import Tortoise
from aerich.utils import compress_dict, decompress_dict, get_models_describe
from app.db.config import TORTOISE_ORM

async def main():
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        state = compress_dict(get_models_describe("models"))
        decompress_dict(state)
        print(state)
    finally:
        await Tortoise.close_connections()

asyncio.run(main())
PY
```

## Runtime File Storage

Uploaded CSV bytes are not stored in the database. `CsvFile.storage_path` points at files under `backend/storage/`, and that directory is ignored by git.

Keep file-backed resources in dedicated models and services when they need quotas, retention, download, or row pagination. Use `ToolSyncItem` only for JSON-shaped tool state.

## Tool Sync Items

Use `tool_sync_items` for authenticated, JSON-shaped per-tool state that does not need a dedicated storage model. The ownership key is:

- `user_id`
- `tool_key`
- `item_key`

That tuple must stay unique. `tool_key` is the module namespace (`mermaid`, `csv`, future tools). `item_key` is stable inside that module (`default`, a document id, or another deterministic key). Store flexible data in `payload` and optional display text in `title`.

**Conventional `payload` fields.** When multiple tools need the same kind of flexible data, keep the JSON key consistent so frontend code can be shared:

| Key | Type | Meaning |
|---|---|---|
| `payload.remark` | `string \| null` | User-supplied free-text note about this archive. Optional. Trimmed by frontend; empty string treated as absent. Surfaced as the second line in history rows. |
| `payload.character_count` | `int` | Mermaid: source character length. Display-only; do not rely on for ordering. |
| `payload.source` | `string` | Mermaid: the raw mermaid source. Drawio: the diagram XML. |

When a tool needs a new shared concept that crosses this convention, add a row here before you start using a new key.

Do not use this table for binary or file-backed resources. CSV files keep `csv_files` because they need quotas, file paths, row pagination, and download behavior.

## Time

The database config sets `use_tz = False` and `timezone = "Asia/Shanghai"`. Current model timestamps are naive datetimes. When deriving application times, match the current pattern unless the project explicitly migrates to timezone-aware storage.

## Avoid

- Staging `backend/storage/`, `.env`, `.venv`, or `__pycache__`.
- Using mutable Python defaults outside ORM field defaults.
- Creating a table per preview tool when `ToolSyncItem` can store stable JSON state.

## Multi-Provider Auth Users

### 1. Scope / Trigger

- Trigger: Adding or changing a login provider, password auth, OAuth callback, or user identity persistence.

### 2. Signatures

- DB: `users.auth_provider VARCHAR(32)`, `users.provider_user_id VARCHAR(128)`, unique index
  `uid_users_provider_user(auth_provider, provider_user_id)`.
- Legacy DB: `users.github_id` remains nullable for compatibility with existing GitHub-created rows.
- DB: `user_auth_accounts(provider, provider_user_id)` identifies one provider account, and
  `user_auth_accounts(user_id, provider)` enforces one account per provider per user in the current product.
- API: `POST /api/v1/auth/login` accepts `{ "username": string, "password": string }`.
- OAuth APIs: `GET /api/v1/auth/{github|linuxdo}/login`, `GET /api/v1/auth/{github|linuxdo}/callback`.
- Account binding APIs: `GET /api/v1/auth/accounts`, `GET /api/v1/auth/{github|linuxdo}/link`,
  `DELETE /api/v1/auth/accounts/{provider}`.
- CLI: `cd backend && uv run python -m app.cli.create_password_user <username> [--email ...] [--password ...]`.

### 3. Contracts

- `auth_provider` values currently used: `password`, `github`, `linuxdo`.
- `users` is the principal identity. `user_auth_accounts` owns login methods. New provider logic should query
  `UserAuthAccount` first and keep `users.auth_provider/provider_user_id/password_hash` as legacy compatibility only.
- For password accounts, `provider_user_id` must equal the local username and `password_hash` must be set on
  `user_auth_accounts`.
- For OAuth accounts, `provider_user_id` must be the provider's stable user id; `password_hash` stays null.
- OAuth login state is a signed payload created with `create_signed_payload()` and includes `purpose`, `redirect`,
  `frontend_origin`, `exp`, and for binding, `user_id`. Do not trust unsigned `state` for account linking.
- Binding start endpoints require Bearer auth and return `{ "url": "<provider authorize URL>" }`; the browser cannot
  navigate directly to these endpoints because top-level navigation does not include the Authorization header.
- Frontend auth callback receives `/#/auth/callback?access_token=<jwt>&redirect=<safe-path>`.
- Env keys: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `LINUXDO_CLIENT_ID`,
  `LINUXDO_CLIENT_SECRET`, optional `LINUXDO_AUTHORIZE_URL`, `LINUXDO_TOKEN_URL`, `LINUXDO_USER_URL`.

### 4. Validation & Error Matrix

- Empty username/password -> `400 请输入账号和密码`.
- Unknown password user or wrong password -> `401 账号或密码错误`.
- OAuth provider missing credentials -> `500 <Provider> OAuth is not configured`.
- OAuth token response without `access_token` -> `400 <Provider> login failed`.
- OAuth profile without stable id -> `400 <Provider> user profile is invalid`.
- Binding a provider already linked to a different user -> `409 该登录方式已绑定到其他账号`.
- Unbinding the last login method -> `400 至少保留一种登录方式`.
- Unbinding password login -> `400 暂不支持解绑账号密码登录`.

### 5. Good/Base/Bad Cases

- Good: existing provider data is backfilled into `user_auth_accounts` during migration and JWT `sub` stays as `users.id`.
- Base: adding a new OAuth provider adds a provider value and reuses `user_auth_accounts(provider, provider_user_id)`.
- Bad: auto-merging two existing users when a provider collision occurs. Return `409` and make merge a deliberate future task.
- Bad: querying users by provider username/email; those fields are mutable and not provider-stable.

### 6. Tests Required

- Run `cd backend && uv run python -m compileall app`.
- Run `cd backend && uv run aerich heads`.
- After migration, run a Tortoise query against `UserAuthAccount` to ensure the new table is readable.
- Verify `POST /api/v1/auth/login` returns `401` instead of `500` after migrations are applied.
- Verify `GET /api/v1/auth/accounts` returns `password`, `github`, and `linuxdo` entries for authenticated users.
- Verify the frontend login page handles normalized request errors without exposing provider internals.

### 7. Wrong vs Correct

Wrong:

```python
await User.update_or_create(github_id=str(profile["id"]), defaults={...})
```

for a new non-GitHub provider.

Correct:

```python
await User.update_or_create(
    auth_provider="linuxdo",
    provider_user_id=str(profile_id),
    defaults={...},
)
```

Wrong:

```javascript
window.location.href = '/api/v1/auth/github/link'
```

for binding a provider from the frontend.

Correct:

```javascript
const response = await createOAuthLinkUrl('github', '/account/security')
window.location.href = response.url
```
