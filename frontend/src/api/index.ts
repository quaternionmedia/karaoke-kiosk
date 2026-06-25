import type { Song, Singer, SessionInfo } from "../types";
import { SONG_CATALOGUE } from "../data/songs";
import { ENV, apiUrl } from "../env";

// ════════════════════════════════════════════════════════════════════
//  API — talks to the FastAPI backend, or a fake "demo" implementation.
//  Selected at startup via ENV.demoMode (see src/env.ts / .env files).
// ════════════════════════════════════════════════════════════════════

export interface StopResult {
  recordingUrl: string | null;
  status: string;
}

export interface ApiClient {
  /** Search the song catalogue. */
  searchSongs(query: string, genre: string): Promise<Song[]>;
  /** Start karaoke playback for the selected song. */
  startPlayback(song: Song, singer: Singer): Promise<SessionInfo>;
  /** Stop playback & end the recording session. */
  stopPlayback(sessionId: string | null): Promise<StopResult>;
  /** Submit the user's email to receive their recording link. */
  submitEmail(email: string, sessionId: string | null): Promise<void>;
}

// ── Shared fetch helper ─────────────────────────────────────────────

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(apiUrl(path), {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status} ${res.statusText}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ── Real backend client ─────────────────────────────────────────────

const realApi: ApiClient = {
  searchSongs(query, genre) {
    const params = new URLSearchParams({ q: query, genre });
    return fetchJson<Song[]>(`/api/songs?${params.toString()}`);
  },

  startPlayback(song, singer) {
    return fetchJson<SessionInfo>("/api/session/start", {
      method: "POST",
      body: JSON.stringify({ songId: song.id, singer }),
    });
  },

  stopPlayback(sessionId) {
    return fetchJson<StopResult>(`/api/session/${sessionId}/stop`, {
      method: "POST",
    });
  },

  async submitEmail(email, sessionId) {
    await fetchJson<void>("/api/recording/share", {
      method: "POST",
      body: JSON.stringify({ email, sessionId }),
    });
  },
};

// ── Demo (fake) client — no backend required ────────────────────────

const DEMO_LATENCY = 250; // ms, to mimic a network round-trip
const delay = <T>(value: T): Promise<T> =>
  new Promise(resolve => setTimeout(() => resolve(value), DEMO_LATENCY));

const demoApi: ApiClient = {
  searchSongs(query, genre) {
    const q = query.toLowerCase();
    return delay(
      SONG_CATALOGUE.filter(
        s =>
          (genre === "All" || s.genre === genre) &&
          (q === "" ||
            s.title.toLowerCase().includes(q) ||
            s.artist.toLowerCase().includes(q)),
      ),
    );
  },

  startPlayback(song, singer) {
    console.info("[demo] startPlayback →", { song, singer });
    return delay({ sessionId: `demo_${Date.now()}`, status: "playing" });
  },

  stopPlayback(sessionId) {
    console.info("[demo] stopPlayback →", sessionId);
    return delay({ recordingUrl: null, status: "finished" });
  },

  submitEmail(email, sessionId) {
    console.info("[demo] submitEmail →", { email, sessionId });
    return delay(undefined);
  },
};

// ── Selected client ─────────────────────────────────────────────────

export const API: ApiClient = ENV.demoMode ? demoApi : realApi;

console.info(
  `[api] mode=${ENV.demoMode ? "demo" : "live"}` +
    (ENV.demoMode ? "" : ` base=${ENV.apiBaseUrl || "(same-origin)"}`),
);
