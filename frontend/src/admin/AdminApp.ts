import m from "mithril";
import { AdminState } from "./state";
import { QueueView } from "./views/Queue";
import { ConfigView } from "./views/Config";
import { TemplatesView } from "./views/Templates";

// ════════════════════════════════════════════════════════════════════
//  ADMIN ROOT — router and main nav
// ════════════════════════════════════════════════════════════════════

const AdminNav = {
  view() {
    return m("nav.admin-nav", [
      m("h1", "Karaoke Admin"),
      m("ul", [
        m("li", m(m.route.Link, { href: "#!/queue" }, "Queue")),
        m("li", m(m.route.Link, { href: "#!/config" }, "Config")),
        m("li", m(m.route.Link, { href: "#!/templates" }, "Templates")),
      ]),
    ]);
  },
};

export const AdminApp = {
  view() {
    return m(".admin-layout", [
      m(AdminNav),
      m(".admin-main", m(m.route.param("page") ? m.route.param("page") : m(QueueView))),
    ]);
  },
};

// Set up routes (hash-based, no server rewrite needed)
m.route(document.body, "#!/queue", {
  "#!/queue": QueueView,
  "#!/config": ConfigView,
  "#!/templates": TemplatesView,
});
