# Unify Tool Archive Copy

## Goal

Make CSV, Mermaid, and Draw.io tool pages use a consistent vocabulary and interaction copy for local work, GitHub login, save actions, and cloud archive lists.

## What I Already Know

- CSV currently uses "历史/最近文件/保存到历史".
- Mermaid currently uses "同步/云端存档/保存/另存为新存档".
- Draw.io currently uses "账号存档/同步/同步到账号/数据".
- All three tools keep local functionality usable without login, and GitHub login only enables cloud persistence.

## Requirements

- Extract a reusable archive/history panel component for tool pages.
- The shared component owns login-checking, logged-out, authenticated list header, refresh, and empty states.
- Tool pages pass their item rows through a slot so CSV, Mermaid, and Draw.io can keep tool-specific metadata and actions.
- Use "云端存档" as the shared name for authenticated saved items across the three tools.
- Use "保存" as the primary persistence action label across the three tools.
- Use consistent login-state copy: local/editor/preview features are usable without login; login only affects cloud archives.
- Use consistent authenticated list headings and empty states.
- Keep tool-specific details only where behavior differs:
  - CSV saves uploaded files as cloud archives.
  - Mermaid saves/updates the current archive and supports "另存为新存档".
  - Draw.io saves the latest exported XML as a new cloud archive snapshot.
- Do not change backend behavior.

## Acceptance Criteria

- [ ] CSV, Mermaid, and Draw.io authenticated list sections use "云端存档".
- [ ] CSV, Mermaid, and Draw.io use the shared archive panel component for login/list/empty states.
- [ ] Primary save buttons use save wording instead of mixed "同步/历史" wording.
- [ ] Logged-out and loading panels have aligned wording.
- [ ] Account sync descriptions use consistent cloud archive terminology.
- [ ] `pnpm lint` and `pnpm build` pass from `frontend/`.

## Out Of Scope

- Changing CSV backend history retention or quotas.
- Adding archive rename UI.
- Changing Draw.io snapshot persistence semantics.
