import m from "mithril";
import { CONFIG } from "../config";
import { State } from "../state";
import { API } from "../api";
import { AppBar } from "./AppBar";

// ── Countdown ──────────────────────────────────────────────────────
export const CountdownScreen = {
  current: CONFIG.countdownFrom,
  key: CONFIG.countdownFrom,   // force animation re-trigger

  oninit() {
    CountdownScreen.current = CONFIG.countdownFrom;
    CountdownScreen.key     = CONFIG.countdownFrom;

    const t = setInterval(() => {
      CountdownScreen.current--;
      CountdownScreen.key = CountdownScreen.current;

      if (CountdownScreen.current <= 0) {
        clearInterval(t);
        CountdownScreen._startPlayback();
      }
      m.redraw();
    }, 1000);
    State._timers.push(t);
  },

  _startPlayback() {
    API.startPlayback(State.song!, { name: State.name, email: State.email })
      .then(session => {
        State.sessionId = session.sessionId;
        State.progress  = 0;
        State.go("playback");
      });
  },

  view() {
    const n = CountdownScreen.current;
    return [
      m(AppBar, { step: "countdown" }),
      m(".screen",
        m(".countdown-wrap",
          // All siblings carry keys so Mithril treats this as a keyed list;
          // the number's key changes each tick to replay the countPop animation.
          m(".countdown-label", { key: "label" }, "Get ready,  " + State.name + "!"),
          n > 0
            ? m(".countdown-number", { key: "num-" + CountdownScreen.key }, n)
            : m(".countdown-number",
                { key: "go", style: "font-size:clamp(3rem,10vw,7rem);letter-spacing:-.01em;" },
                "GO! 🎤"
              ),
          m("p.countdown-song", { key: "song" },
            m("span", State.song!.title),
            m("span.countdown-artist", " — " + State.song!.artist)
          )
        )
      )
    ];
  }
};
