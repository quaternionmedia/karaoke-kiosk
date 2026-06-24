import type { Song, Singer, SessionInfo } from "../types";
import { SONG_CATALOGUE } from "../data/songs";

// ════════════════════════════════════════════════════════════════════
//  API HOOKS — wire these up to your REST endpoints
// ════════════════════════════════════════════════════════════════════

export interface StopResult {
  recordingUrl: string | null;
  status: string;
}

export const API = {
  /**
   * Search the song catalogue.
   * @param query  - user search text
   * @param genre  - genre filter (or "All")
   * @returns array of song objects
   */
  searchSongs(query: string, genre: string): Promise<Song[]> {
    // TODO: replace stub with → fetch(`/api/songs?q=${encodeURIComponent(query)}&genre=${genre}`)
    //        .then(r => r.json())
    const q = query.toLowerCase();
    return Promise.resolve(
      SONG_CATALOGUE.filter(s =>
        (genre === "All" || s.genre === genre) &&
        (q === "" || s.title.toLowerCase().includes(q) || s.artist.toLowerCase().includes(q))
      )
    );
  },

  /**
   * Start karaoke playback for the selected song.
   * @param song     - song object { id, title, artist, … }
   * @param singer   - { name, email }
   * @returns session info { sessionId, … }
   */
  startPlayback(song: Song, singer: Singer): Promise<SessionInfo> {
    // TODO: replace stub with → fetch('/api/session/start', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ songId: song.id, singer })
    // }).then(r => r.json())
    console.info("[API] startPlayback →", { song, singer });
    return Promise.resolve({ sessionId: `sess_${Date.now()}`, status: "playing" });
  },

  /**
   * Stop playback & end the recording session.
   */
  stopPlayback(sessionId: string | null): Promise<StopResult> {
    // TODO: replace stub with → fetch(`/api/session/${sessionId}/stop`, { method: 'POST' })
    //        .then(r => r.json())
    console.info("[API] stopPlayback →", sessionId);
    return Promise.resolve({ recordingUrl: null, status: "finished" });
  },

  /**
   * Submit the user's email to receive their recording link.
   */
  submitEmail(email: string, sessionId: string | null): Promise<void> {
    // TODO: replace stub with → fetch('/api/recording/share', {
    //   method: 'POST',
    //   body: JSON.stringify({ email, sessionId })
    // })
    console.info("[API] submitEmail →", { email, sessionId });
    return Promise.resolve();
  },
};
