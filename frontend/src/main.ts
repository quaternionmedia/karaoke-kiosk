import m from "mithril";
import "./styles/global.css";
import { App } from "./components/App";
import { CONFIG } from "./config";
import { apiUrl } from "./env";

// ════════════════════════════════════════════════════════════════════
//  FETCH CONFIG FROM BACKEND
// ════════════════════════════════════════════════════════════════════
(async () => {
  try {
    const res = await fetch(apiUrl("/api/venue"));
    if (res.ok) {
      const venueCfg = await res.json();
      Object.assign(CONFIG, {
        venueName: venueCfg.venue_name,
        venueMessage: venueCfg.venue_message,
        splashDelay: venueCfg.splash_delay,
        countdownFrom: venueCfg.countdown_from,
        thankYouDuration: venueCfg.thank_you_duration,
      });
      console.info("[config] loaded from /api/venue");
    }
  } catch (e) {
    console.warn("[config] failed to load from /api/venue, using defaults", e);
  }
  
  // ════════════════════════════════════════════════════════════════════
  //  MOUNT
  // ════════════════════════════════════════════════════════════════════
  m.mount(document.getElementById("app")!, App);
})();
