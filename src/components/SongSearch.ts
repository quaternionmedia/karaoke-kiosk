import m from "mithril";
import { State } from "../state";
import { API } from "../api";
import { GENRES, SONG_CATALOGUE } from "../data/songs";
import type { Song } from "../types";
import { AppBar } from "./AppBar";

// ── Song Search ────────────────────────────────────────────────────
export const SongSearch = {
  query:   "",
  genre:   "All",
  results: [...SONG_CATALOGUE] as Song[],
  loading: false,

  oninit() {
    SongSearch.query   = "";
    SongSearch.genre   = "All";
    SongSearch.results = [...SONG_CATALOGUE];
    SongSearch.loading = false;
  },

  doSearch() {
    SongSearch.loading = true;
    API.searchSongs(SongSearch.query, SongSearch.genre).then(results => {
      SongSearch.results = results;
      SongSearch.loading = false;
      m.redraw();
    });
  },

  selectSong(song: Song) {
    State.song  = song;
    State.name  = "";
    State.email = "";
    State.go("userinfo");
  },

  view() {
    const { query, genre, results, loading } = SongSearch;
    return [
      m(AppBar, { step: "search" }),
      m(".screen", { style: "padding-top:1rem;padding-bottom:1rem;" },
        m(".search-screen",

          // Header
          m(".search-header",
            m("h2", "🎵 Pick Your Song"),
            m("span", { style: "color:var(--muted);font-size:.9rem;" },
              results.length + " available"
            )
          ),

          // Search bar
          m(".search-bar-wrap",
            m("span.search-icon", "🔍"),
            m("input[type=text]", {
              placeholder: "Search title or artist…",
              value: query,
              oninput(e: Event) {
                SongSearch.query = (e.target as HTMLInputElement).value;
                SongSearch.doSearch();
              }
            })
          ),

          // Genre filters
          m(".genre-filters",
            GENRES.map(g =>
              m("button.genre-btn", {
                class: genre === g ? "active" : "",
                onclick() {
                  SongSearch.genre = g;
                  SongSearch.doSearch();
                }
              }, g)
            )
          ),

          // Song list
          loading
            ? m(".no-results", m(".emoji","⏳"), m("span","Searching…"))
            : results.length === 0
              ? m(".no-results",
                  m(".emoji","😕"),
                  m("span","No songs found. Try a different search.")
                )
              : m(".song-list",
                  results.map((song, i) =>
                    m(".song-card", {
                      key: song.id,
                      onclick: () => SongSearch.selectSong(song),
                    },
                      m(".song-num", i + 1),
                      m(".song-info",
                        m(".song-title", song.title),
                        m(".song-artist", song.artist)
                      ),
                      m(".song-meta",
                        m(".song-duration", song.duration),
                        m("span.genre-tag", {
                          style: `background:${song.color}22;color:${song.color};`
                        }, song.genre)
                      )
                    )
                  )
                )
        )
      )
    ];
  }
};
