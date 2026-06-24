import m from "mithril";
import { CONFIG } from "../config";
import type { Song, ViewName } from "../types";

// ════════════════════════════════════════════════════════════════════
//  APP STATE
// ════════════════════════════════════════════════════════════════════

interface AppState {
  view: ViewName;
  song: Song | null;
  name: string;
  email: string;
  sessionId: string | null;
  countdown: number;
  progress: number;       // 0–100 playback progress
  _timers: number[];      // internal timer handles
  clearTimers(): void;
  go(view: ViewName): void;
}

export const State: AppState = {
  view:        "splash",
  song:        null,
  name:        "",
  email:       "",
  sessionId:   null,
  countdown:   CONFIG.countdownFrom,
  progress:    0,
  _timers:     [],

  clearTimers() {
    this._timers.forEach(clearInterval);
    this._timers = [];
  },

  go(view) {
    this.clearTimers();
    this.view = view;
    m.redraw();
  },
};
