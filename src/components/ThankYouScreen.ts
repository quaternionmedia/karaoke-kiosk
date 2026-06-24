import m from "mithril";
import { CONFIG } from "../config";
import { State } from "../state";

// ── Thank You Screen ───────────────────────────────────────────────
export const ThankYouScreen = {
  oninit() {
    const t = setTimeout(() => State.go("splash"), CONFIG.thankYouDuration);
    State._timers.push(t);
  },
  view() {
    const pct = CONFIG.thankYouDuration / 1000;
    return m(".screen",
      m(".thankyou-wrap",
        m(".confetti-icon", "🌟"),
        m("h1.thankyou-title", "Bravo!"),
        m("p.thankyou-sub",
          "Amazing performance, ",
          m("span.thankyou-name", State.name), "! ",
          "The crowd loved it. ",
          State.email
            ? "We'll send your recording to " + State.email + " shortly! 📧"
            : "Ask the staff for your recording! 🎬"
        ),
        m(".restart-bar",
          m(".pulse-dot"),
          m("span", `Starting over in ${pct}s…`)
        ),
        m("button.btn.btn-ghost.btn-sm",
          { onclick: () => State.go("splash") },
          "Start Over Now"
        )
      )
    );
  }
};
