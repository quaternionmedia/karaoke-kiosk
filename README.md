# Rock Star Video

Karaoke Kiosk — a single-page kiosk app built with [Mithril.js](https://mithril.js.org/), bundled with [Vite](https://vitejs.dev/) and written in TypeScript.

## Getting started

```bash
npm install      # install dependencies
npm run dev      # start the Vite dev server (HMR)
npm run build    # type-check + production build to dist/
npm run preview  # serve the production build locally
```

## Structure

```
index.html              # entry HTML, mounts #app
src/
  main.ts               # app entry — imports styles, mounts <App>
  config.ts             # kiosk CONFIG (venue name, timings)
  types.ts              # shared types (Song, Singer, ViewName, …)
  data/songs.ts         # GENRES + mock SONG_CATALOGUE
  api/index.ts          # API stubs — wire to real REST endpoints (see TODOs)
  state/index.ts        # central App State + view router state machine
  components/            # one Mithril component per screen
  styles/global.css      # all styling
```

The flow is a state machine: **splash → search → user info → countdown → playback → thank you**, then it loops back to the splash screen.

To connect a real backend, replace the stubbed `fetch` calls in [src/api/index.ts](src/api/index.ts) (each method documents the intended endpoint).
