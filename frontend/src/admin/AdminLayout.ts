import m from "mithril";

// ════════════════════════════════════════════════════════════════════
//  ADMIN LAYOUT — nav bar + main content area
// ════════════════════════════════════════════════════════════════════

export const AdminLayout = {
  view(vnode: any) {
    return m(".admin-layout", [
      m("nav.admin-nav", [
        m("h1", "🎤 Karaoke Admin"),
        m("ul", [
          m("li", m(m.route.Link, { href: "/queue" }, "Queue")),
          m("li", m(m.route.Link, { href: "/config" }, "Config")),
          m("li", m(m.route.Link, { href: "/templates" }, "Templates")),
        ]),
      ]),
      m(".admin-main", vnode.children),
    ]);
  },
};
