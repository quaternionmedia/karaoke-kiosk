import m from "mithril";
import "../styles/global.css";
import "./styles.css";
import { AdminLayout } from "./AdminLayout";
import { QueueView } from "./views/Queue";
import { ConfigView } from "./views/Config";
import { TemplatesView } from "./views/Templates";

// ════════════════════════════════════════════════════════════════════
//  ROUTING (hash-based by default, no server rewrites needed)
// ════════════════════════════════════════════════════════════════════
m.route(document.getElementById("app")!, "/queue", {
  "/queue": { render: () => m(AdminLayout, m(QueueView)) },
  "/config": { render: () => m(AdminLayout, m(ConfigView)) },
  "/templates": { render: () => m(AdminLayout, m(TemplatesView)) },
});

// Mithril uses hash routing by default, so URLs will be:
// http://localhost:5173/admin.html#!/queue
// http://localhost:5173/admin.html#!/config
// http://localhost:5173/admin.html#!/templates
