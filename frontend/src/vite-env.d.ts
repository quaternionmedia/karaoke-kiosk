/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the backend API, e.g. "http://localhost:8000".
   *  Leave empty to use same-origin relative requests (e.g. behind a proxy). */
  readonly VITE_API_BASE_URL?: string;
  /** "true" / "1" to use the in-browser demo (fake) API instead of the backend. */
  readonly VITE_DEMO_MODE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
