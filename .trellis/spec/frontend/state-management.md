# State Management

> How state is managed in this project.

---

## Overview

<!--
Document your project's state management conventions here.

Questions to answer:
- What state management solution do you use?
- How is local vs global state decided?
- How do you handle server state?
- What are the patterns for derived state?
-->

(To be filled by the team)

---

## State Categories

<!-- Local state, global state, server state, URL state -->

(To be filled by the team)

---

## When to Use Global State

<!-- Criteria for promoting state to global -->

(To be filled by the team)

---

## Server State

<!-- How server data is cached and synchronized -->

### Account Sync

Use `useAccountSync(toolKey, { itemKey })` for logged-in account synchronization shared by tool pages.

* `toolKey` must match the backend `/sync/items/{tool_key}` namespace.
* `itemKey` defaults to `default` and should be stable for the synced document.
* Call `loadItem()` to hydrate local tool state after auth initialization.
* Call `saveItem({ title, payload })` to persist JSON-shaped state.
* If the tool owns files or binary data, keep its domain-specific API and use `useAccountSync()` only for login/sync UI state.

Mermaid uses generic sync for source text. CSV keeps `csvFiles.js` for file history because the backend owns upload quotas, storage paths, and row pagination.

---

## Common Mistakes

<!-- State management mistakes your team has made -->

(To be filled by the team)
