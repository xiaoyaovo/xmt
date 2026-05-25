# Database Guidelines

> Database patterns and conventions for this project.

---

## Overview

<!--
Document your project's database conventions here.

Questions to answer:
- What ORM/query library do you use?
- How are migrations managed?
- What are the naming conventions for tables/columns?
- How do you handle transactions?
-->

(To be filled by the team)

---

## Query Patterns

<!-- How should queries be written? Batch operations? -->

(To be filled by the team)

---

## Migrations

<!-- How to create and run migrations -->

### Tool Sync Items

Use `tool_sync_items` for authenticated, JSON-shaped per-tool state that does not need a dedicated storage model. The ownership key is:

* `user_id`
* `tool_key`
* `item_key`

The tuple must stay unique. `tool_key` is the module namespace (`mermaid`, `csv`, future tools). `item_key` is stable inside that module (`default`, a document id, or another deterministic key). Store flexible data in `payload` and optional display text in `title`.

Do not use this table for binary/file-backed resources. CSV files keep their dedicated `csv_files` storage because they need quotas, file paths, row pagination, and download behavior.

---

## Naming Conventions

<!-- Table names, column names, index names -->

(To be filled by the team)

---

## Common Mistakes

<!-- Database-related mistakes your team has made -->

(To be filled by the team)
