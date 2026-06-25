// ════════════════════════════════════════════════════════════════════
//  ENVIRONMENT — backend address + demo toggle (from Vite env vars)
// ════════════════════════════════════════════════════════════════════
//
// Configure via a .env file (see .env.example):
//   VITE_API_BASE_URL  — backend origin, e.g. "http://localhost:8000".
//                        Leave empty for same-origin "/api" requests.
//   VITE_DEMO_MODE     — "true"/"1" to use the in-browser fake API.

function asBool(value: string | undefined): boolean {
  return value === "true" || value === "1";
}

export interface KioskEnv {
  /** Backend origin without a trailing slash ("" = same-origin). */
  apiBaseUrl: string;
  /** When true, the app uses the fake demo API instead of the backend. */
  demoMode: boolean;
}

export const ENV: KioskEnv = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, ""),
  demoMode: asBool(import.meta.env.VITE_DEMO_MODE),
};

/** Build a full API URL from a path like "/api/songs". */
export function apiUrl(path: string): string {
  return `${ENV.apiBaseUrl}${path}`;
}
