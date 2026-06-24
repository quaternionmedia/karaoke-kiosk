// ════════════════════════════════════════════════════════════════════
//  SHARED TYPES
// ════════════════════════════════════════════════════════════════════

export interface Song {
  id: number;
  title: string;
  artist: string;
  genre: string;
  duration: string; // "M:SS"
  color: string;    // hex
}

export interface Singer {
  name: string;
  email: string;
}

export interface SessionInfo {
  sessionId: string;
  status: string;
}

export type ViewName =
  | "splash"
  | "search"
  | "userinfo"
  | "countdown"
  | "playback"
  | "thankyou";
