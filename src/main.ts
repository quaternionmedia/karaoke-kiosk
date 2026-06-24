import m from "mithril";
import "./styles/global.css";
import { App } from "./components/App";

// ════════════════════════════════════════════════════════════════════
//  MOUNT
// ════════════════════════════════════════════════════════════════════
m.mount(document.getElementById("app")!, App);
