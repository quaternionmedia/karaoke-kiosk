import m from "mithril";
import * as api from "../api";
import { queueWs } from "../ws";

// ════════════════════════════════════════════════════════════════════
//  QUEUE VIEW
// ════════════════════════════════════════════════════════════════════

interface QueueViewState {
  queue: api.PerformanceRead[];
  songs: api.SongRead[];
  venues: api.VenueRead[];
  selectedVenueId: number | null;
  enqueueFormState: {
    songId: number | null;
    name: string;
    email: string;
  };
  isLoading: boolean;
  wsConnected: boolean;
}

export const QueueView = {
  state: {
    queue: [],
    songs: [],
    venues: [],
    selectedVenueId: null,
    enqueueFormState: { songId: null, name: "", email: "" },
    isLoading: false,
    wsConnected: false,
  } as QueueViewState,

  oninit: async (vnode: any) => {
    const state = vnode.state as QueueViewState;

    // Load initial data
    state.isLoading = true;
    try {
      [state.venues, state.songs, state.queue] = await Promise.all([
        api.listVenues(),
        api.listSongs(),
        api.listQueue(),
      ]);
      if (state.venues.length > 0) {
        state.selectedVenueId = state.venues[0].id;
      }
    } catch (e) {
      console.error("Failed to load queue data:", e);
    } finally {
      state.isLoading = false;
    }

    // Connect to WebSocket
    try {
      await queueWs.connect();
      state.wsConnected = true;

      queueWs.onUpdate(async (msg) => {
        if (msg.type === "queue.changed") {
          // Refetch queue
          try {
            state.queue = await api.listQueue(state.selectedVenueId || undefined);
            m.redraw();
          } catch (e) {
            console.error("Failed to refetch queue:", e);
          }
        }
      });
    } catch (e) {
      console.error("Failed to connect to WebSocket:", e);
    }
  },

  oncreate: (vnode: any) => {
    const state = vnode.state as QueueViewState;
    // Set up automatic reconnection cleanup on destroy
    vnode._removeWsListener = () => {
      queueWs.disconnect();
    };
  },

  onbeforeremove: (vnode: any) => {
    if (vnode._removeWsListener) {
      vnode._removeWsListener();
    }
  },

  view: (vnode: any) => {
    const state = vnode.state as QueueViewState;

    return m(".queue-view", [
      m("h2", "Performance Queue"),

      // Connection indicator
      m(
        ".ws-indicator",
        { class: state.wsConnected ? "connected" : "disconnected" },
        state.wsConnected ? "● Connected" : "○ Disconnected"
      ),

      // Enqueue form
      m(".enqueue-form", [
        m("h3", "Add to Queue"),

        m("div", [
          m("label", "Venue"),
          m(
            "select",
            {
              value: state.selectedVenueId || "",
              onchange: (e: Event) => {
                state.selectedVenueId = parseInt(
                  (e.target as HTMLSelectElement).value,
                  10
                );
              },
            },
            state.venues.map((v) =>
              m("option", { value: v.id }, v.name)
            )
          ),
        ]),

        m("div", [
          m("label", "Song"),
          m(
            "select",
            {
              value: state.enqueueFormState.songId || "",
              onchange: (e: Event) => {
                state.enqueueFormState.songId = parseInt(
                  (e.target as HTMLSelectElement).value,
                  10
                );
              },
            },
            [
              m("option", { value: "" }, "Select a song..."),
              ...state.songs.map((s) =>
                m(
                  "option",
                  { value: s.id },
                  `${s.name} — ${s.artist}`
                )
              ),
            ]
          ),
        ]),

        m("div", [
          m("label", "Singer Name"),
          m("input", {
            type: "text",
            placeholder: "Name",
            value: state.enqueueFormState.name,
            oninput: (e: Event) => {
              state.enqueueFormState.name = (e.target as HTMLInputElement).value;
            },
          }),
        ]),

        m("div", [
          m("label", "Email"),
          m("input", {
            type: "email",
            placeholder: "email@example.com",
            value: state.enqueueFormState.email,
            oninput: (e: Event) => {
              state.enqueueFormState.email = (e.target as HTMLInputElement).value;
            },
          }),
        ]),

        m(
          "button.btn.btn-primary",
          {
            onclick: async () => {
              try {
                await api.enqueuePerformance(
                  state.enqueueFormState.songId!,
                  state.enqueueFormState.name,
                  state.enqueueFormState.email,
                  state.selectedVenueId || undefined
                );
                state.enqueueFormState = { songId: null, name: "", email: "" };
                state.queue = await api.listQueue(
                  state.selectedVenueId || undefined
                );
              } catch (e) {
                alert("Failed to enqueue: " + e);
              }
            },
          },
          "Enqueue"
        ),
      ]),

      // Queue table
      m(
        ".queue-table",
        state.queue.length === 0
          ? m("p", "Queue is empty")
          : m("table", [
              m("thead", [
                m("tr", [
                  m("th", "#"),
                  m("th", "Singer"),
                  m("th", "Song"),
                  m("th", ""),
                ]),
              ]),
              m(
                "tbody",
                state.queue.map((perf, idx) => {
                  const song = state.songs.find((s) => s.id === perf.song_id);
                  return m("tr", [
                    m("td", perf.queue_position),
                    m("td", "Performer " + perf.performer_id),
                    m("td", song?.name || "Unknown"),
                    m("td", [
                      idx > 0
                        ? m(
                            "button.btn.btn-sm",
                            { onclick: async () => {
                              try {
                                await api.movePerformance(perf.id, idx - 1);
                                state.queue = await api.listQueue(
                                  state.selectedVenueId || undefined
                                );
                              } catch (e) {
                                alert("Failed to move: " + e);
                              }
                            } },
                            "↑"
                          )
                        : null,
                      idx < state.queue.length - 1
                        ? m(
                            "button.btn.btn-sm",
                            { onclick: async () => {
                              try {
                                await api.movePerformance(perf.id, idx + 1);
                                state.queue = await api.listQueue(
                                  state.selectedVenueId || undefined
                                );
                              } catch (e) {
                                alert("Failed to move: " + e);
                              }
                            } },
                            "↓"
                          )
                        : null,
                      m(
                        "button.btn.btn-sm",
                        { onclick: async () => {
                          try {
                            await api.removePerformance(perf.id);
                            state.queue = await api.listQueue(
                              state.selectedVenueId || undefined
                            );
                          } catch (e) {
                            alert("Failed to remove: " + e);
                          }
                        } },
                        "✕"
                      ),
                    ]),
                  ]);
                })
              ),
            ])
      ),

      // Start next button
      m(
        "button.btn.btn-primary",
        {
          onclick: async () => {
            try {
              await api.startNext(state.selectedVenueId || undefined);
              state.queue = await api.listQueue(
                state.selectedVenueId || undefined
              );
            } catch (e) {
              alert("Failed to start next: " + e);
            }
          },
        },
        "▶ Start Next"
      ),
    ]);
  },
};
