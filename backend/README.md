# Karaoke Kiosk — Backend

FastAPI + SQLModel administrative backend for the karaoke kiosk. It persists
venues, events, performers, songs, and performances; serves the endpoints the
singer-facing frontend expects; provides admin CRUD; and fires lifecycle hooks
(OBS scene switching / recording / email) through an in-process event bus.

## Layout

```
src/kiosk/
  app.py        FastAPI factory (create_app): CORS, routers, lifespan, event bus
  main.py       uvicorn entrypoint (app = create_app())
  config.py     pydantic-settings Settings + get_settings()
  db.py         engine + get_session() dependency
  enums.py      status enumerations
  models/       SQLModel tables (Venue, Event, Performer, Song, Tag,
                Performance, Recording, EmailTemplate)
  schemas/      request/response DTOs (SongRead matches the frontend shape)
  services/     business logic: performances, queue, email_templates, etc.
  events/       EventBus, signal payloads, OBS/email/WebSocket handlers
  routers/      API routers mounted under /api
migrations/     Alembic environment + versions
tests/          pytest suite
```

## Bootstrap

```bash
cd backend
uv sync                                   # install runtime + dev deps
uv run alembic upgrade head               # create/upgrade the SQLite schema
uv run uvicorn kiosk.main:app --reload --port 8000
uv run pytest                             # run tests
```

After changing models, generate a migration:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

## Frontend contract

The kiosk frontend (`../frontend`) calls these endpoints:

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/songs?q=&genre=` | Search songs; `genre=All` means no filter |
| POST | `/api/session/start` | `{songId, singer:{name,email}}` → `{sessionId, status}` |
| POST | `/api/session/{sessionId}/stop` | → `{recordingUrl, status}` |
| POST | `/api/recording/share` | `{email, sessionId}` → 204 |
| GET | `/api/venue` | Public kiosk config (venue name, timings, welcome message) |

## Admin API

The admin dashboard (`../frontend/admin.html`) uses these endpoints (all require `X-Admin-Key` header when `ADMIN_API_KEY` is set):

### Queue (realtime admin-only walk-up enqueueing)
| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/admin/queue?event_id=` | List queued performances, ordered |
| POST | `/api/admin/queue` | Enqueue `{songId, singer, eventId?}` |
| POST | `/api/admin/queue/{id}/move` | `{toIndex}` reorder in queue |
| DELETE | `/api/admin/queue/{id}` | Remove from queue |
| POST | `/api/admin/queue/start-next` | Promote head to PLAYING, fire hooks |
| WS | `/api/admin/queue/ws` | WebSocket for realtime nudges (`{type:"queue.changed"}`) |

### Email Templates (per-venue)
| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/admin/email-templates?venue_id=` | List templates |
| POST | `/api/admin/email-templates` | Create (validates placeholders) |
| GET/PATCH/DELETE | `/api/admin/email-templates/{id}` | Manage individual |
| POST | `/api/admin/email-templates/{id}/preview` | Render with sample data |

### Configuration
| Method | Path | Notes |
| --- | --- | --- |
| PATCH | `/api/admin/venues/{id}` | Edit kiosk config (timings, messages) |
| GET | `/api/admin/settings` | Read env config (secrets masked) |

### Other
Standard CRUD under `/api/admin/{events,performers,performances,songs,venues}`.

## Configuration

All settings come from the environment (or a `.env` file).

### Kiosk config (editable via admin dashboard)
- Lives in the `Venue` row (name, location, welcome message, timings).
- Served by `GET /api/venue` so the kiosk app can use live values.

### Infrastructure settings (env-only, read-only in admin dashboard)
- `DATABASE_URL` (default `sqlite:///./kiosk.db`)
- `CORS_ORIGINS` (defaults to the Vite dev server origins)
- `OBS_ENABLED` / `OBS_WS_URL` / `OBS_WS_PASSWORD` — OBS integration
- `EMAIL_ENABLED` / `SMTP_*` — email sending (for recording shares)
- `RECORDING_BASE_URL` — turns OBS file paths into shareable URLs
- `ADMIN_API_KEY` — when set, admin routes require an `X-Admin-Key` header

### WebSocket support
- Requires `websockets` dev dependency (see `pyproject.toml`).
- For production, use `uvicorn[standard]` to get WebSocket support.
- Queue updates broadcast via `/api/admin/queue/ws`; clients reconnect with exponential backoff.
