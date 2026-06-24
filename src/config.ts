// ════════════════════════════════════════════════════════════════════
//  CONFIG — edit these to customise the kiosk
// ════════════════════════════════════════════════════════════════════

export interface Config {
  venueName: string;
  venueMessage: string;
  splashDelay: number;      // ms before "tap to start" prompt appears
  countdownFrom: number;    // countdown seconds before playback
  thankYouDuration: number; // ms on thank-you screen before restart
}

export const CONFIG: Config = {
  venueName:    "Neon Nights Karaoke",
  venueMessage: "Welcome! Step up to the mic and let your inner star shine. Choose a song, enter your name, and get ready to rock the house! 🎤",
  splashDelay:  3500,
  countdownFrom: 3,
  thankYouDuration: 5000,
};
