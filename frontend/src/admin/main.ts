import m from "mithril";
import "../styles/global.css";
import "./styles.css";
import { AdminLayout } from "./AdminLayout";
import { QueueView } from "./views/Queue";
import { ConfigView } from "./views/Config";
import { TemplatesView } from "./views/Templates";

// ════════════════════════════════════════════════════════════════════
//  ROUTING
// ════════════════════════════════════════════════════════════════════
m.route(document.getElementById("app")!, "/queue", {
  "/queue": { render: () => m(AdminLayout, m(QueueView)) },
  "/config": { render: () => m(AdminLayout, m(ConfigView)) },
  "/templates": { render: () => m(AdminLayout, m(TemplatesView)) },
});
