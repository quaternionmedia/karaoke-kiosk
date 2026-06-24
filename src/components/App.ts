import m from "mithril";
import { State } from "../state";
import { SplashScreen } from "./SplashScreen";
import { SongSearch } from "./SongSearch";
import { UserInfoForm } from "./UserInfoForm";
import { CountdownScreen } from "./CountdownScreen";
import { PlaybackScreen } from "./PlaybackScreen";
import { ThankYouScreen } from "./ThankYouScreen";

// ════════════════════════════════════════════════════════════════════
//  ROOT COMPONENT  — state-machine router
// ════════════════════════════════════════════════════════════════════
export const App = {
  view() {
    switch (State.view) {
      case "splash":    return m(SplashScreen);
      case "search":    return m(SongSearch);
      case "userinfo":  return m(UserInfoForm);
      case "countdown": return m(CountdownScreen);
      case "playback":  return m(PlaybackScreen);
      case "thankyou":  return m(ThankYouScreen);
      default:          return m(SplashScreen);
    }
  }
};
