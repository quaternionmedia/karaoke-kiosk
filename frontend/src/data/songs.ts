import type { Song } from "../types";

// ════════════════════════════════════════════════════════════════════
//  MOCK SONG CATALOGUE  (replace with real API call — see api/index.ts)
// ════════════════════════════════════════════════════════════════════

export const GENRES = ["All", "Pop", "Rock", "R&B", "Country", "80s", "Hip-Hop"];

export const SONG_CATALOGUE: Song[] = [
  { id: 1,  title: "Bohemian Rhapsody",      artist: "Queen",            genre: "Rock",   duration: "5:55", color: "#f59e0b" },
  { id: 2,  title: "Sweet Caroline",          artist: "Neil Diamond",     genre: "Pop",    duration: "3:27", color: "#22c55e" },
  { id: 3,  title: "Livin' on a Prayer",      artist: "Bon Jovi",         genre: "Rock",   duration: "4:10", color: "#f59e0b" },
  { id: 4,  title: "Don't Stop Believin'",    artist: "Journey",          genre: "Rock",   duration: "4:10", color: "#f59e0b" },
  { id: 5,  title: "I Will Always Love You",  artist: "Whitney Houston",  genre: "R&B",    duration: "4:32", color: "#c026d3" },
  { id: 6,  title: "Wonderwall",              artist: "Oasis",            genre: "Rock",   duration: "4:19", color: "#f59e0b" },
  { id: 7,  title: "Africa",                  artist: "Toto",             genre: "80s",    duration: "4:55", color: "#7c3aed" },
  { id: 8,  title: "Take On Me",              artist: "a-ha",             genre: "80s",    duration: "3:46", color: "#7c3aed" },
  { id: 9,  title: "Shallow",                 artist: "Lady Gaga & Bradley Cooper", genre: "Pop", duration: "3:35", color: "#22c55e" },
  { id: 10, title: "Friends in Low Places",   artist: "Garth Brooks",     genre: "Country",duration: "4:17", color: "#d97706" },
  { id: 11, title: "Blinding Lights",         artist: "The Weeknd",       genre: "Pop",    duration: "3:22", color: "#22c55e" },
  { id: 12, title: "Lose Yourself",           artist: "Eminem",           genre: "Hip-Hop",duration: "5:26", color: "#3b82f6" },
  { id: 13, title: "Purple Rain",             artist: "Prince",           genre: "R&B",    duration: "8:41", color: "#c026d3" },
  { id: 14, title: "Hotel California",        artist: "Eagles",           genre: "Rock",   duration: "6:31", color: "#f59e0b" },
  { id: 15, title: "Jolene",                  artist: "Dolly Parton",     genre: "Country",duration: "2:42", color: "#d97706" },
  { id: 16, title: "Girls Just Want to Have Fun", artist: "Cyndi Lauper", genre: "80s",   duration: "3:57", color: "#7c3aed" },
  { id: 17, title: "Shape of You",            artist: "Ed Sheeran",       genre: "Pop",    duration: "3:54", color: "#22c55e" },
  { id: 18, title: "Mr. Brightside",          artist: "The Killers",      genre: "Rock",   duration: "3:42", color: "#f59e0b" },
];
