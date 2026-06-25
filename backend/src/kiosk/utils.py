"""Small pure helpers shared across services and schemas."""

from __future__ import annotations

# Default accent colors keyed by genre, mirroring the frontend's convention
# where a song's color tracks its genre (frontend/src/data/songs.ts).
GENRE_COLORS: dict[str, str] = {
    "Pop": "#22c55e",
    "Rock": "#f59e0b",
    "R&B": "#a855f7",
    "Country": "#eab308",
    "80s": "#ec4899",
    "Hip-Hop": "#3b82f6",
}
DEFAULT_COLOR = "#64748b"


def format_duration(seconds: int | None) -> str:
    """Format a duration in seconds as ``"M:SS"`` (empty string if unknown)."""
    if seconds is None:
        return ""
    minutes, secs = divmod(max(seconds, 0), 60)
    return f"{minutes}:{secs:02d}"


def color_for_genre(genre: str | None) -> str:
    """Return the default accent color for a genre."""
    if genre is None:
        return DEFAULT_COLOR
    return GENRE_COLORS.get(genre, DEFAULT_COLOR)
