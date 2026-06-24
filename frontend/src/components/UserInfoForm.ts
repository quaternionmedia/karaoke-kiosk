import m from "mithril";
import { State } from "../state";
import { AppBar } from "./AppBar";

// ── User Info Form ─────────────────────────────────────────────────
export const UserInfoForm = {
  nameErr: false,

  oninit() { UserInfoForm.nameErr = false; },

  submit() {
    if (!State.name.trim()) {
      UserInfoForm.nameErr = true;
      m.redraw();
      return;
    }
    State.go("countdown");
  },

  view() {
    const song = State.song!;
    return [
      m(AppBar, { step: "userinfo" }),
      m(".screen",
        m(".info-card",

          m("h2", { style: "font-size:1.4rem;font-weight:800;" }, "🎙️ Tell Us Your Name"),

          // Selected song banner
          m(".selected-song-banner",
            m(".ssb-icon", "🎵"),
            m("div",
              m(".ssb-title", song.title),
              m(".ssb-artist", song.artist)
            )
          ),

          // Name field
          m(".field",
            m("label.label", { for: "singer-name" }, "Your Name"),
            m("input[type=text]#singer-name", {
              placeholder: "e.g. Alex",
              value: State.name,
              style: UserInfoForm.nameErr ? "border-color:var(--danger);" : "",
              oninput(e: Event) {
                State.name = (e.target as HTMLInputElement).value;
                UserInfoForm.nameErr = false;
              }
            }),
            UserInfoForm.nameErr && m("span", {
              style: "color:var(--danger);font-size:.8rem;"
            }, "Please enter your name to continue.")
          ),

          // Email field
          m(".field",
            m("label.label", { for: "singer-email" },
              "Email Address",
              m("span.optional-badge", "Optional")
            ),
            m("input[type=email]#singer-email", {
              placeholder: "Get your recording link sent here",
              value: State.email,
              oninput(e: Event) { State.email = (e.target as HTMLInputElement).value; }
            })
          ),

          // Actions
          m(".form-actions",
            m("button.btn.btn-ghost",
              { onclick: () => State.go("search") },
              "← Back"
            ),
            m("button.btn.btn-primary",
              { onclick: UserInfoForm.submit },
              "Ready to Sing! 🎤"
            )
          ),

          State.email && m("p.privacy-note",
            "📧 We'll send your recording to " + State.email + " when the song ends."
          )
        )
      )
    ];
  }
};
