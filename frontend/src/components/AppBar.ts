import m from "mithril";
import { CONFIG } from "../config";

interface AppBarAttrs {
  step: string;
}

// ── App Bar ────────────────────────────────────────────────────────
export const AppBar: m.Component<AppBarAttrs> = {
  view({ attrs: { step } }) {
    const steps = ["search", "userinfo", "countdown", "playback"];
    return m(".app-bar",
      m(".app-bar-logo", "🎤 " + CONFIG.venueName),
      m(".step-indicator",
        steps.map((s, i) =>
          m(".step-dot", {
            class: s === step ? "active"
                 : steps.indexOf(step) > i ? "done" : ""
          })
        )
      )
    );
  }
};
