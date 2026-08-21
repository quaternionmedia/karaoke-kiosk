# Rock Star Video

Karaoke Kiosk — a single-page kiosk app built with [Mithril.js](https://mithril.js.org/), bundled with [Vite](https://vitejs.dev/) and written in TypeScript.

## Getting started

```bash
npm install      # install dependencies
npm run dev      # start the Vite dev server (HMR) on port 5173
               # — serves both the kiosk (/) and admin (/admin.html)
npm run build    # type-check + production build to dist/
               # — emits both index.html and admin.html
npm run preview  # serve the production build locally
```

## Structure

### Kiosk (singer-facing app)

```
index.html              # entry HTML, mounts #app → kiosk
src/
  main.ts               # kiosk entry; hydrates CONFIG from /api/venue
  config.ts             # kiosk CONFIG — name, timings (defaults only)
  types.ts              # shared types (Song, Singer, ViewName, …)
  data/songs.ts         # GENRES + mock SONG_CATALOGUE
  api/index.ts          # API client (kiosk-facing + reusable fetchJson)
  env.ts                # backend URL resolution + demo mode
  state/index.ts        # central App State + view state machine
  components/            # one Mithril component per screen
  styles/global.css      # design tokens, shared UI classes
```

The kiosk flow is a state machine: **splash → search → user info → countdown → playback → thank you**, then loops back. It fetches live config from `GET /api/venue` on startup, so changes in the admin dashboard are live.

### Admin Dashboard

```
admin.html              # entry HTML, mounts admin app
src/admin/
  main.ts               # admin entry — sets up m.route
  AdminLayout.ts        # nav bar + content area
  state.ts              # shared admin state
  api.ts                # admin API client (queue, templates, config, settings)
  ws.ts                 # WebSocket handler for realtime queue updates
  styles.css            # admin-specific styles (tables, forms)
  views/
    Queue.ts            # enqueue, reorder, remove, start-next
    Config.ts           # edit venue settings, view env config (masked)
    Templates.ts        # manage per-venue email templates + preview
```

The admin dashboard shares the kiosk's `global.css` (tokens, buttons) and uses Mithril's hash-based router (no server rewrite needed).
