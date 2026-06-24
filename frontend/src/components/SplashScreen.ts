import m from "mithril";
import { CONFIG } from "../config";
import { State } from "../state";

// ── Splash Screen ──────────────────────────────────────────────────
export const SplashScreen = {
  ready: false,
  oninit() {
    SplashScreen.ready = false;
    const t = setTimeout(() => {
      SplashScreen.ready = true;
      m.redraw();
    }, CONFIG.splashDelay);
    State._timers.push(t);
  },
  view() {
    return m(".screen",
      m(".splash-wrap",
        m(".splash-icon", "🎤"),
        m(".logo-text", CONFIG.venueName),
        m(".logo-sub", "Karaoke Kiosk"),
        m("p.venue-message", CONFIG.venueMessage),
        SplashScreen.ready
          ? m(".splash-cta",
              m("button.btn.btn-primary.btn-lg",
                { onclick: () => State.go("search") },
                "✨ Choose a Song"
              )
            )
          : m(".splash-cta",
              m("span", { style: "color:var(--muted);font-size:.9rem;" },
                m(".pulse-dot"), " Loading…"
              )
            )
      )
    );
  }
};
