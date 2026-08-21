# Admin Dashboard — Implementation Plan

## Context

The kiosk has a FastAPI/SQLModel backend with a **substantial admin API already
built** (`/api/admin/*` for venues, events, performers, performances, songs) and a
Mithril/Vite singer-facing SPA with **no admin UI**. We need a dashboard for
(1) configuration settings, (2) the performer queue, (3) per-venue email templates.

Decisions taken:

| # | Decision |
|---|---|
| Queue | **Admin-only.** Kiosk flow unchanged; the MC enqueues walk-ups and hits "start next". |
| Email templates | **New `EmailTemplate` table**, many per venue. |
| Env settings | **Read-only, secrets masked.** |
| Auth | **Disabled for now** — `admin_guard` already no-ops when `ADMIN_API_KEY` is unset. Keep the guard on routes so enabling it is a one-env-var change. |
| UI | **Share the existing frontend app** — second Vite entry, no new toolchain. |
| Realtime | **WebSocket** for queue updates. |

## What already exists (reuse, do not rebuild)

| Need | Where |
|---|---|
| Admin CRUD API | `backend/src/kiosk/routers/{venues,events,performers,performances,songs}.py` |
| Admin auth guard | `admin_guard` — `backend/src/kiosk/deps.py` |
| Venue = live kiosk config | `Venue`: `welcome_message`, `splash_delay_ms`, `countdown_from`, `thank_you_duration_ms`, `obs_ws_*`, `is_active` |
| Public config endpoint | `GET /api/venue` → `VenueConfig` (`schemas/venue.py`) |
| Get-or-create singer | `get_or_create_performer()` — `services/performers.py` |
| Cancel a performance | `cancel_performance()` — `services/performances.py` |
| Handler registration pattern | `events/handlers/__init__.py` `register_default_handlers(bus, settings)`, mirrors `obs.py` / `email.py` |
| Sync pub/sub bus | `EventBus` — `events/bus.py` (exception-isolating) |
| Test harness | `backend/tests/conftest.py` — in-memory SQLite, `client`, `venue`, `songs`, `events_log` fixtures |
| Frontend fetch helper | `fetchJson()` in `frontend/src/api/index.ts` (currently module-private — export it) |
| API base URL resolution | `apiUrl()` / `ENV` — `frontend/src/env.ts` |
| CSS design tokens | `:root`, `.btn`, `.btn-primary`, `.btn-sm`, `.label` — `frontend/src/styles/global.css` |

## Approach

### 1. Queue (the only genuinely missing domain logic)

`PerformanceStatus.QUEUED` exists in `enums.py` but **nothing ever creates a queued
performance** — `start_performance()` jumps straight to `PLAYING`, and there is no
ordering column.

- Add `Performance.queue_position: int | None` (indexed, null once playing/finished).
- New `services/queue.py`: `list_queue`, `enqueue`, `move`, `remove`, `start_next`.
- **Refactor, don't copy:** extract the tail of `start_performance()` (create pending
  `Recording` + emit `PERFORMANCE_STARTED`) into a shared `_begin(session, bus,
  performance, venue_id)`. Both the kiosk path and `start_next` route through it, so
  OBS/recording hooks fire identically for a queued performance. Copying that block
  into `start_next` would silently give queued singers no recording.
- `move` renumbers the whole list on each reorder.
  `# ponytail: O(n) renumber per move, fine for a bar queue; switch to fractional ranks past ~1k rows`

### 2. Realtime via the existing event bus

Rather than making the queue routes reach into WebSocket code, follow the established
handler pattern:

- New signal `QUEUE_CHANGED = "queue.changed"` + `QueueChanged(event_id)` dataclass in
  `events/signals.py`.
- New `events/handlers/ws.py` → `QueueBroadcaster`, registered in
  `register_default_handlers` next to `ObsHandler` / `EmailHandler`.
- **Sync → async bridge:** routes are sync `def` (threadpool), broadcast is async.
  Capture `asyncio.get_running_loop()` in the `create_app` lifespan and store it on the
  broadcaster; each connected socket owns an `asyncio.Queue`; `publish()` does
  `loop.call_soon_threadsafe(q.put_nowait, msg)`. ~35 lines, no new dependency.
- **Broadcast a nudge, not a snapshot:** the message is `{"type": "queue.changed"}` and
  the client refetches `GET /api/admin/queue`. The handler has no DB session, so
  serialising a full snapshot would mean opening one outside the request lifecycle —
  ten lines instead of forty, and no stale-payload ordering bugs.
- `websockets` must be added to the dev deps: plain `uvicorn` (no `[standard]`) rejects
  WS upgrades. Starlette's `TestClient.websocket_connect` runs in-process and needs
  nothing extra.

### 3. Email templates

New table, and **migrate the two existing `Venue` columns into it and drop them** —
leaving both in place would mean two sources of truth for the same email.

- `models/email_template.py`: `id`, `venue_id` (FK, indexed), `slug`, `name`, `subject`,
  `body`, `is_active`; unique `(venue_id, slug)`.
- Migration copies `Venue.email_subject_template`/`email_body_template` into a
  `slug="recording_share"` row per venue, then drops both columns via
  `batch_alter_table` (SQLite can't `DROP COLUMN` directly).
- `_build_share_email()` looks up `recording_share` for the venue, falling back to
  module-level `DEFAULT_SHARE_SUBJECT`/`DEFAULT_SHARE_BODY`.
- **Not lazy here — two real bugs in the current rendering:**
  - `subject_tpl.format(**ctx)` raises `KeyError` at *send* time on a typo'd
    placeholder, inside a bus handler that swallows it. Render with
    `format_map(defaultdict(str, ctx))` and catch `ValueError` for malformed braces, so
    a bad template can never break the send pipeline.
  - Validate placeholders **on save** (POST/PATCH → 422 listing unknown names) against
    `ALLOWED_PLACEHOLDERS = {name, song, recording_url, venue}`. Failing in the editor
    beats failing silently at 2am.
- `POST /api/admin/email-templates/{id}/preview` renders with sample context, reusing
  the same `render()` the sender uses — one implementation, so the preview cannot lie.

### 4. Config settings

- `Venue` row stays the live-editable config, edited through the **existing**
  `PATCH /api/admin/venues/{id}`. No new endpoint.
- `GET /api/admin/settings` returns the env-level `Settings` read-only with secrets
  masked (`"••••"` when set, `null` when unset).
- Mask via an **explicit** `SECRET_FIELDS` frozenset (`smtp_password`, `obs_ws_password`,
  `admin_api_key`, `database_url`), not a name-suffix heuristic — a heuristic that
  misses a future secret field is a credential leak.
- Wire the kiosk to `/api/venue`: `frontend/src/main.ts` fetches it at boot and
  overlays `CONFIG`, falling back to the hardcoded values on failure. Without this,
  editing config in the dashboard changes nothing on the kiosk screen.

### 5. Dashboard UI

Second Vite entry inside the existing frontend — one line of config, zero new deps.

- `frontend/admin.html` + `src/admin/`; `vite.config.ts` gets
  `build.rollupOptions.input = { main: "index.html", admin: "admin.html" }`.
- Routing with `m.route` (Mithril is already a dependency). Hash mode by default, so no
  server rewrite rules needed.
- Export `fetchJson` from `src/api/index.ts` and reuse it, plus `apiUrl()` from
  `src/env.ts`. The admin client stays separate from `ApiClient` — that interface is the
  kiosk contract and carries the demo-mode fake.
- Reuse the `:root` tokens and `.btn*` classes from `global.css`; add a small
  `src/admin/styles.css` for tables and forms only.

## Files to modify

**Backend — new**
- `src/kiosk/models/email_template.py`
- `src/kiosk/schemas/{queue,email_template,settings}.py`
- `src/kiosk/services/{queue,email_templates}.py`
- `src/kiosk/routers/{queue,email_templates,settings}.py`
- `src/kiosk/events/handlers/ws.py`
- `migrations/versions/<rev>_queue_and_email_templates.py`
- `tests/test_queue.py`, `tests/test_email_templates.py`, `tests/test_admin_ws.py`, `tests/test_admin_settings.py`

**Backend — edit**
- `src/kiosk/models/performance.py` — `queue_position`
- `src/kiosk/models/venue.py` — drop the two template columns
- `src/kiosk/models/__init__.py` — register `EmailTemplate`
- `src/kiosk/schemas/{venue,performance}.py` — drop template fields / add `queue_position`
- `src/kiosk/services/performances.py` — extract `_begin()`, rework `_build_share_email()`
- `src/kiosk/events/signals.py` — `QUEUE_CHANGED` + payload
- `src/kiosk/events/handlers/__init__.py` — register `QueueBroadcaster`
- `src/kiosk/app.py` — capture the loop in lifespan
- `src/kiosk/routers/__init__.py` — mount the three new routers
- `pyproject.toml` — `websockets` dev dep
- `README.md` — document the new endpoints

**Frontend — new**
- `admin.html`, `src/admin/{main,api,ws}.ts`, `src/admin/views/{Queue,Config,Templates}.ts`, `src/admin/styles.css`

**Frontend — edit**
- `vite.config.ts` — two entries
- `src/api/index.ts` — export `fetchJson`
- `src/main.ts` + `src/config.ts` — hydrate CONFIG from `/api/venue`
- `README.md`

## API surface added

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/admin/queue?event_id=` | Queued performances, ordered |
| POST | `/api/admin/queue` | Enqueue `{songId, singer:{name,email}, eventId?}` |
| POST | `/api/admin/queue/{id}/move` | `{toIndex}` reorder |
| DELETE | `/api/admin/queue/{id}` | Cancel + drop from queue |
| POST | `/api/admin/queue/start-next` | Promote head to `PLAYING`, fire hooks |
| WS | `/api/admin/queue/ws` | `{"type":"queue.changed"}` nudges |
| GET/POST | `/api/admin/email-templates?venue_id=` | List / create |
| GET/PATCH/DELETE | `/api/admin/email-templates/{id}` | Read / update / delete |
| POST | `/api/admin/email-templates/{id}/preview` | Render with sample context |
| GET | `/api/admin/settings` | Env settings, secrets masked |

## Steps

**Backend**
- [ ] Add `queue_position` to `Performance`; add `EmailTemplate` model + register it in `models/__init__.py`; remove the two template columns from `Venue`.
- [ ] Write the Alembic migration: add column, create table, backfill `recording_share` rows from the old venue columns, drop them with `batch_alter_table`.
- [ ] Extract `_begin()` in `services/performances.py`; confirm `start_performance()` behaviour is unchanged (existing tests must pass untouched).
- [ ] Write `services/queue.py` (`list_queue`, `enqueue`, `move`, `remove`, `start_next`), emitting `QUEUE_CHANGED` on every mutation.
- [ ] Write `services/email_templates.py`: CRUD, `validate_placeholders()`, `render()`; repoint `_build_share_email()` at it with module-level defaults.
- [ ] Add `QUEUE_CHANGED` signal + `QueueBroadcaster` handler; capture the event loop in the `create_app` lifespan; register the handler.
- [ ] Add the three routers + schemas; mount them in `routers/__init__.py`.
- [ ] Leave the WS route unguarded with `# ponytail: WS unauthenticated; browsers can't set X-Admin-Key — move to a query-param or subprotocol token when ADMIN_API_KEY is enabled`.
- [ ] Add `websockets` to the dev dependency group.
- [ ] Tests: queue ordering/lifecycle (assert `PERFORMANCE_STARTED` fires on `start-next`), template CRUD + 422 on bad placeholder + fallback rendering, WS nudge on enqueue, settings masking.

**Frontend**
- [ ] Add `admin.html`, the two-entry `vite.config.ts`, and `src/admin/main.ts` with `m.route`.
- [ ] Export `fetchJson`; write `src/admin/api.ts` on top of it and `apiUrl()`.
- [ ] Queue view: table, enqueue form (song picker from `/api/admin/songs`), move up/down, remove, "Start next".
- [ ] `src/admin/ws.ts`: connect, refetch on nudge, reconnect with backoff, show a connection indicator.
- [ ] Config view: venue form → `PATCH /api/admin/venues/{id}`; read-only masked env settings table.
- [ ] Templates view: venue picker → template list → subject/body editor, placeholder chips, preview pane.
- [ ] Hydrate kiosk `CONFIG` from `/api/venue` in `main.ts`, falling back to hardcoded values.
- [ ] Update both READMEs.

## Verification

- [ ] `cd backend && uv run pytest` — existing suite green (proves the `_begin()` refactor and the venue-column drop broke nothing) plus the four new test modules.
- [ ] `cd backend && uv run alembic upgrade head` on a DB with existing venue template values; confirm they land as `recording_share` rows. Check `downgrade()` too.
- [ ] `cd frontend && npm run build` — `tsc` must type-check clean and emit both `index.html` and `admin.html`.
- [ ] Manual: `uv run uvicorn kiosk.main:app --reload --port 8000` + `npm run dev`; open `/admin.html`.
  - Enqueue three singers, reorder, remove one, "Start next" → the promoted row leaves the queue and a `Recording` row exists for it.
  - Open the queue in two browser tabs; mutate in one, confirm the other updates without a refresh. Kill and restart the backend, confirm the socket reconnects.
  - Edit `countdown_from` in Config, reload the kiosk, confirm the countdown changes.
  - Save a template containing `{bogus}` → 422 in the UI; a valid one previews and is used by the share email (visible in the `[email:stub]` log line).

## Deliberately skipped

- Real auth (per decision) — the guard stays wired, so it is one env var away.
- Editing SMTP/OBS creds from the UI; they stay env-only and masked.
- Frontend test framework — none exists today; `npm run build` type-checks and the logic lives in the tested backend.
