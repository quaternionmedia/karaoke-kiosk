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
                Performance, Recording)
  schemas/      request/response DTOs (SongRead matches the frontend shape)
  services/     business logic + performance lifecycle (fires hooks)
  events/       EventBus, signal payloads, OBS/email handlers (stubs)
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

The frontend (`../frontend`) calls these endpoints (see `frontend/src/api/index.ts`):

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/songs?q=&genre=` | `genre=All` means no filter |
| POST | `/api/session/start` | `{songId, singer:{name,email}}` → `{sessionId, status}` |
| POST | `/api/session/{sessionId}/stop` | → `{recordingUrl, status}` |
| POST | `/api/recording/share` | `{email, sessionId}` → 204 |

Plus admin CRUD under `/api/admin/*` and a public `GET /api/venue` returning the
kiosk config (so the frontend can eventually drop its hardcoded `config.ts`).

## Configuration

All settings come from the environment (or a `.env` file). Key flags:

- `DATABASE_URL` (default `sqlite:///./kiosk.db`)
- `CORS_ORIGINS` (defaults to the Vite dev server origins)
- `OBS_ENABLED` / `EMAIL_ENABLED` — when false (default), the OBS and email
  handlers log their intended actions instead of performing them.
- `ADMIN_API_KEY` — when set, admin routes require an `X-Admin-Key` header.
