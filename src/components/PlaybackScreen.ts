import m from "mithril";
import { State } from "../state";
import { API } from "../api";
import { AppBar } from "./AppBar";

// ── Playback / Recording ───────────────────────────────────────────
export const PlaybackScreen = {
  elapsed: 0,           // seconds elapsed
  totalSec: 0,
  waveHeights: Array(8).fill(0).map(() => Math.random()),

  oninit() {
    PlaybackScreen.elapsed   = 0;
    PlaybackScreen.totalSec  = PlaybackScreen._parseDuration(State.song!.duration);
    State.progress = 0;

    // Animate waveform heights
    const wt = setInterval(() => {
      PlaybackScreen.waveHeights = PlaybackScreen.waveHeights.map(() =>
        6 + Math.random() * 26
      );
      m.redraw();
    }, 180);

    // Progress tick
    const pt = setInterval(() => {
      PlaybackScreen.elapsed++;
      State.progress = Math.min(
        100,
        (PlaybackScreen.elapsed / PlaybackScreen.totalSec) * 100
      );
      if (State.progress >= 100) {
        clearInterval(pt);
        clearInterval(wt);
        PlaybackScreen._finish();
      }
      m.redraw();
    }, 1000);

    State._timers.push(wt, pt);
  },

  _parseDuration(str: string): number {
    const [min, sec] = str.split(":").map(Number);
    return min * 60 + sec;
  },

  _fmt(sec: number): string {
    const min = Math.floor(sec / 60);
    const s = sec % 60;
    return `${min}:${String(s).padStart(2, "0")}`;
  },

  _finish() {
    API.stopPlayback(State.sessionId).then(() => {
      if (State.email) API.submitEmail(State.email, State.sessionId);
      State.go("thankyou");
    });
  },

  view() {
    const { elapsed, totalSec, waveHeights } = PlaybackScreen;
    const remaining = Math.max(0, totalSec - elapsed);

    return [
      m(AppBar, { step: "playback" }),
      m(".screen", { style: "padding-top:1rem;" },
        m(".playback-wrap",

          // Now playing badge
          m(".now-playing-header",
            m(".rec-dot"), "Now Performing"
          ),

          // Stage (video/lyrics placeholder)
          m(".stage-display",
            m(".stage-placeholder", "🎬"),
            m("span.stage-api-badge", "Playback API"),
            m(".stage-api-note",
              "Lyrics & video will render here via your playback API. ",
              "Hook ", m("code", { style: "color:var(--accent);" }, "API.startPlayback()"),
              " to stream content."
            )
          ),

          // Song + singer info
          m(".playback-info",
            m("div",
              m(".pb-song",  State.song!.title),
              m(".pb-artist",State.song!.artist),
              m(".pb-singer","🎤 " + State.name)
            ),
            // Live waveform
            m(".waveform",
              waveHeights.map((h, i) =>
                m("span", { key: i, style: `height:${h}px;` })
              )
            )
          ),

          // Progress bar
          m(".progress-bar-wrap",
            m(".progress-times",
              m("span", PlaybackScreen._fmt(elapsed)),
              m("span", "−" + PlaybackScreen._fmt(remaining))
            ),
            m(".progress-track",
              m(".progress-fill", { style: `width:${State.progress}%` })
            )
          ),

          // Controls
          m(".playback-controls",
            m("button.btn.btn-ghost.btn-sm",
              {
                title: "Stop early",
                onclick() { State.clearTimers(); PlaybackScreen._finish(); }
              },
              "⏹ Finish Early"
            )
          )
        )
      )
    ];
  }
};
