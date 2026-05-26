# Deploy draw.io Service

## Goal

Deploy a self-hosted draw.io / diagrams.net service for Xinming so the frontend can iframe the editor from the user's own server instead of `https://embed.diagrams.net`, with support for both diagram and whiteboard-style embed modes.

The task has expanded to include the Xinming integration shape: XinmingTools should no longer embed draw.io inside the ordinary tool detail page. The tools list should link directly into dedicated fullscreen diagram and whiteboard iframe wrappers, while Xinming owns save, autosave, file history, and account-backed persistence through the existing backend sync APIs.

## What I Already Know

- The current frontend embeds `https://embed.diagrams.net` in `frontend/src/pages/tools/DrawioPage.vue`.
- The existing URL uses `ui=min`, which gives the standard diagram editor experience.
- Whiteboard mode can use the same embed endpoint with `ui=sketch&sketch=1` plus `rough` / `toSketch` load options.
- The repository does not currently include Docker Compose, Nginx, or deployment scripts.
- Local SSH config has a server alias `sg` for `root@152.42.201.71:22`.
- Non-interactive SSH access to `sg` now works with public key authentication.
- Server runs Ubuntu 24.04.3 LTS, Docker 29.4.0, Docker Compose v5.1.2, and Caddy v2.11.2.
- Deployed draw.io container is named `drawio` and binds `127.0.0.1:8090 -> 8080`.
- Existing `cxmjtt.com` Caddy site now proxies `/drawio/*` to draw.io.
- The first subpath proxy attempt stripped `/drawio`, causing draw.io to load only the editor shell while shape/stencil/canvas resources failed or stalled.
- Fixed by mounting draw.io inside Tomcat at `/drawio` and preserving the `/drawio` prefix through Caddy.
- `drawio.cxmjtt.com` now resolves to the server and Caddy has obtained a Let's Encrypt certificate.
- The current `DrawioPage.vue` combines three responsibilities: tool entry, iframe editor, and account-backed history.
- Existing account sync helpers already support generic per-tool items through `useAccountSync('drawio')`.
- The preferred second-development pattern from comparable projects is iframe embed mode plus host-owned save/history, not a deep draw.io source fork.

## Assumptions

- Deploying via Docker is preferred because diagrams.net publishes the `jgraph/drawio` image.
- The draw.io service should run behind HTTPS on an existing domain or subdomain.
- The frontend will later be updated to use the self-hosted draw.io origin.

## Open Questions

- Resolved for MVP: the fullscreen wrapper lives under Xinming at `/tools/drawio/editor`. `drawio.cxmjtt.com/` remains the raw draw.io service entry for now.

## Requirements

- Run self-hosted draw.io using the official Docker image.
- Expose the service through HTTPS.
- Keep container restart behavior persistent across reboots.
- Leave room for both standard diagram embed and whiteboard/sketch embed URLs.
- Verify the deployed `/` and embed URL respond successfully.
- Link directly from `/tools` to the fullscreen Draw.io and whiteboard editor modes.
- Keep `/tools/drawio` as a compatibility redirect to the diagram editor.
- Add a dedicated fullscreen draw.io wrapper page for editing diagrams and whiteboards.
- Keep the iframe protocol boundary explicit: pinned origin, defensive message parsing, load after `init`, export/save/autosave handling, and status reset after successful persistence.
- Reuse Xinming account sync for draw.io XML persistence in the MVP.
- Document the future backend/file-history model before adding any new storage tables.

## Acceptance Criteria

- [x] `docker ps` shows a healthy draw.io container on the server.
- [x] Public HTTPS URL loads the full draw.io editor via `https://cxmjtt.com/drawio/`.
- [x] Embed URL works with `embed=1&proto=json&ui=min`.
- [x] Whiteboard embed URL works with `embed=1&proto=json&ui=sketch&sketch=1`.
- [x] Frontend origin changed from `https://embed.diagrams.net` to the deployed URL.
- [x] `/tools` links directly to diagram editor and whiteboard editor without mounting draw.io iframe.
- [x] `/tools/drawio` redirects to the diagram editor for compatibility.
- [x] `/tools/drawio/editor` opens a fullscreen iframe wrapper that occupies the available viewport on desktop, tablet, and phone.
- [x] The fullscreen wrapper can load starter XML, request export, save to the existing draw.io sync bucket, open/delete history entries, and clear draw.io's modified state after save.
- [x] The implementation plan for shared backend persistence and a future history/file page is documented.

## Definition Of Done

- Server deployment completed and verified.
- Deployment commands/config recorded.
- Frontend follow-up noted if not included in this task.
- Rollback command available.

## Out Of Scope

- Changing the frontend integration in this deployment-only step unless explicitly requested.
- Implementing draw.io document storage inside the draw.io container; Xinming already handles XML sync separately.
- Forking or rebuilding draw.io source code.
- Replacing the existing generic account sync backend with dedicated draw.io tables in the MVP.
- Real-time collaborative editing.

## Research References

- [`research/drawio-deployment.md`](research/drawio-deployment.md) — self-hosted Docker/Caddy deployment details and working URLs.
- [`research/drawio-integration-patterns.md`](research/drawio-integration-patterns.md) — comparable project patterns; recommends Xinming-owned fullscreen wrapper plus host-owned persistence.

## Integration Plan

### Phase 1: Split Tool List From Editor

- Keep `/tools` as the XinmingTools entry point.
- Link the Draw.io row directly to `/tools/drawio/editor?mode=diagram`.
- Add a separate whiteboard row linking directly to `/tools/drawio/editor?mode=whiteboard`.
- Keep `/tools/drawio` as a compatibility redirect to diagram mode.
- Move the iframe/postMessage/save/history implementation into `/tools/drawio/editor`.
- Use query parameters for mode:
  - `/tools/drawio/editor?mode=diagram`
  - `/tools/drawio/editor?mode=whiteboard`

### Phase 2: Fullscreen Wrapper Behavior

- The editor route should be a fullscreen application surface, not a card inside a normal page.
- The outer page should control:
  - fixed top toolbar
  - save/export/history actions
  - login prompt when needed
  - error and saving status
  - `overflow: hidden`
  - iframe height based on `100dvh` minus toolbar height
  - mobile safe-area padding
- The iframe should use:
  - diagram mode: `https://drawio.cxmjtt.com/drawio/?embed=1&proto=json&spin=1&ui=min&lang=zh&libraries=1&saveAndExit=0&noSaveBtn=0&noExitBtn=1`
  - whiteboard mode: `https://drawio.cxmjtt.com/drawio/?embed=1&proto=json&spin=1&ui=sketch&sketch=1&lang=zh&libraries=1&saveAndExit=0&noSaveBtn=0&noExitBtn=1`

### Phase 3: MVP Persistence

- Reuse the existing generic sync backend:
  - tool key: `drawio`
  - item key: generated archive key
  - payload: `{ xml, xml_length, archive_key, mode, updated_from, remark }`
- Save flow:
  - manual save opens `ToolSaveDialog`
  - confirm triggers draw.io `export`
  - host persists returned XML
  - host sends draw.io `status` with `modified: false`
- Autosave flow:
  - listen for draw.io `autosave`
  - update local XML state
  - defer cloud writes unless/until product decision confirms autosave should create versions

### Phase 4: History/File Page

- Add `/tools/drawio/files` when file management becomes first-class.
- Read from the same backend sync items for the MVP.
- Show compact rows with:
  - title
  - mode badge (`图表` / `白板`)
  - updated time
  - remark
  - open/delete actions
- Later backend upgrade path:
  - `drawio_files`: file id, owner id, title, mode, latest version, timestamps
  - `drawio_versions`: version id, file id, XML blob/ref, remark, created_by, created_at
  - optional object storage if XML payloads become large

## Recommended MVP

Implement Phase 1 through Phase 3 first. Keep Phase 4 as a documented follow-up unless the user explicitly asks to build the history page in this same pass.

## Technical Notes

- Official container image: `jgraph/drawio`.
- Default container ports are typically HTTP `8080` and HTTPS `8443`.
- Deployed local binding behind reverse proxy: `127.0.0.1:8090 -> container 8080`.
- Docker Compose file lives at `/opt/drawio/docker-compose.yml` on `sg`.
- A mounted `/opt/drawio/server.xml` changes Tomcat context from root `/` to `/drawio`.
- Working URL: `https://drawio.cxmjtt.com/drawio/?embed=1&proto=json&ui=min&lang=zh`.
- Working whiteboard URL: `https://drawio.cxmjtt.com/drawio/?embed=1&proto=json&ui=sketch&sketch=1&lang=zh`.
- Direct editor check URL: `https://drawio.cxmjtt.com/drawio/?ui=min&lang=zh&libraries=1`.
- Frontend source now uses `https://drawio.cxmjtt.com/drawio/` for the iframe embed and opens the non-embed URL in a new window.
- Frontend draw.io URLs include `lang=zh` for Chinese UI.
- `https://drawio.cxmjtt.com/` redirects to `/drawio/?lang=zh&ui=min&libraries=1` so users can enter the root domain directly without hitting the Tomcat 404.
