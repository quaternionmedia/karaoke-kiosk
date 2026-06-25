"""Song DTOs. ``SongRead`` matches the frontend Song shape exactly."""

from __future__ import annotations

from pydantic import BaseModel

from kiosk.models.song import Song
from kiosk.utils import color_for_genre, format_duration


class SongRead(BaseModel):
    """Shape consumed by the frontend (frontend/src/types.ts)."""

    id: int
    title: str
    artist: str
    genre: str
    duration: str  # "M:SS"
    color: str  # hex

    @classmethod
    def from_song(cls, song: Song) -> "SongRead":
        return cls(
            id=song.id,
            title=song.name,
            artist=song.artist,
            genre=song.genre or "",
            duration=format_duration(song.duration_seconds),
            color=song.color or color_for_genre(song.genre),
        )


class SongCreate(BaseModel):
    name: str
    artist: str
    genre: str | None = None
    duration_seconds: int | None = None
    color: str | None = None
    is_active: bool = True
    tags: list[str] = []


class SongUpdate(BaseModel):
    name: str | None = None
    artist: str | None = None
    genre: str | None = None
    duration_seconds: int | None = None
    color: str | None = None
    is_active: bool | None = None
    tags: list[str] | None = None


class SongAdminRead(BaseModel):
    """Full DB representation for admin tooling."""

    id: int
    name: str
    artist: str
    genre: str | None
    duration_seconds: int | None
    color: str | None
    is_active: bool
    tags: list[str] = []
