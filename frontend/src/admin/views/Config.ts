import m from "mithril";
import * as api from "../api";

// ════════════════════════════════════════════════════════════════════
//  CONFIG VIEW
// ════════════════════════════════════════════════════════════════════

interface ConfigViewState {
  venues: api.VenueRead[];
  settings: api.SettingsRead | null;
  selectedVenueId: number | null;
  editingVenue: api.VenueRead | null;
  isLoading: boolean;
}

export const ConfigView = {
  state: {
    venues: [],
    settings: null,
    selectedVenueId: null,
    editingVenue: null,
    isLoading: false,
  } as ConfigViewState,

  oninit: async (vnode: any) => {
    const state = vnode.state as ConfigViewState;

    state.isLoading = true;
    try {
      [state.venues, state.settings] = await Promise.all([
        api.listVenues(),
        api.getSettings(),
      ]);
      if (state.venues.length > 0) {
        state.selectedVenueId = state.venues[0].id;
        state.editingVenue = { ...state.venues[0] };
      }
    } catch (e) {
      console.error("Failed to load config:", e);
    } finally {
      state.isLoading = false;
    }
  },

  view: (vnode: any) => {
    const state = vnode.state as ConfigViewState;

    if (state.isLoading) {
      return m(".config-view", "Loading...");
    }

    return m(".config-view", [
      m("h2", "Configuration"),

      // Venue picker
      m("div", [
        m("h3", "Kiosk Settings"),
        m("label", "Venue"),
        m(
          "select",
          {
            value: state.selectedVenueId || "",
            onchange: async (e: Event) => {
              const venueId = parseInt(
                (e.target as HTMLSelectElement).value,
                10
              );
              state.selectedVenueId = venueId;
              const venue = state.venues.find((v) => v.id === venueId);
              if (venue) {
                state.editingVenue = { ...venue };
              }
            },
          },
          state.venues.map((v) => m("option", { value: v.id }, v.name))
        ),
      ]),

      // Venue form
      state.editingVenue
        ? m(".venue-form", [
            m("div", [
              m("label", "Venue Name"),
              m("input", {
                type: "text",
                value: state.editingVenue.name,
                oninput: (e: Event) => {
                  if (state.editingVenue) {
                    state.editingVenue.name = (e.target as HTMLInputElement)
                      .value;
                  }
                },
              }),
            ]),

            m("div", [
              m("label", "Welcome Message"),
              m("textarea", {
                value: state.editingVenue.welcome_message || "",
                oninput: (e: Event) => {
                  if (state.editingVenue) {
                    state.editingVenue.welcome_message = (e.target as HTMLTextAreaElement)
                      .value || null;
                  }
                },
              }),
            ]),

            m("div", [
              m("label", "Splash Delay (ms)"),
              m("input", {
                type: "number",
                value: state.editingVenue.splash_delay_ms,
                oninput: (e: Event) => {
                  if (state.editingVenue) {
                    state.editingVenue.splash_delay_ms = parseInt(
                      (e.target as HTMLInputElement).value,
                      10
                    );
                  }
                },
              }),
            ]),

            m("div", [
              m("label", "Countdown From (seconds)"),
              m("input", {
                type: "number",
                value: state.editingVenue.countdown_from,
                oninput: (e: Event) => {
                  if (state.editingVenue) {
                    state.editingVenue.countdown_from = parseInt(
                      (e.target as HTMLInputElement).value,
                      10
                    );
                  }
                },
              }),
            ]),

            m("div", [
              m("label", "Thank You Duration (ms)"),
              m("input", {
                type: "number",
                value: state.editingVenue.thank_you_duration_ms,
                oninput: (e: Event) => {
                  if (state.editingVenue) {
                    state.editingVenue.thank_you_duration_ms = parseInt(
                      (e.target as HTMLInputElement).value,
                      10
                    );
                  }
                },
              }),
            ]),

            m(
              "button.btn.btn-primary",
              {
                onclick: async () => {
                  if (!state.editingVenue) return;
                  try {
                    await api.updateVenue(state.editingVenue.id, {
                      name: state.editingVenue.name,
                      welcome_message: state.editingVenue.welcome_message,
                      splash_delay_ms: state.editingVenue.splash_delay_ms,
                      countdown_from: state.editingVenue.countdown_from,
                      thank_you_duration_ms:
                        state.editingVenue.thank_you_duration_ms,
                    });
                    alert("Saved!");
                  } catch (e) {
                    alert("Failed to save: " + e);
                  }
                },
              },
              "Save"
            ),
          ])
        : null,

      // Environment settings (read-only)
      state.settings
        ? m(".settings-table", [
            m("h3", "Environment Settings (Read-only)"),
            m("table", [
              m("thead", [
                m("tr", [
                  m("th", "Setting"),
                  m("th", "Value"),
                ]),
              ]),
              m("tbody", [
                m("tr", [
                  m("td", "Database"),
                  m("td", state.settings.database_url || "(not set)"),
                ]),
                m("tr", [
                  m("td", "OBS Enabled"),
                  m("td", state.settings.obs_enabled ? "Yes" : "No"),
                ]),
                m("tr", [
                  m("td", "Email Enabled"),
                  m("td", state.settings.email_enabled ? "Yes" : "No"),
                ]),
                m("tr", [
                  m("td", "SMTP Host"),
                  m("td", state.settings.smtp_host || "(not set)"),
                ]),
                m("tr", [
                  m("td", "Recording Base URL"),
                  m("td", state.settings.recording_base_url || "(not set)"),
                ]),
                m("tr", [
                  m("td", "Admin Key Set"),
                  m("td", state.settings.admin_api_key ? "Yes" : "No"),
                ]),
              ]),
            ]),
          ])
        : null,
    ]);
  },
};
