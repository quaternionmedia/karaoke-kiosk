"""Song endpoints: public search (frontend) + admin CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard
from kiosk.schemas.song import SongAdminRead, SongCreate, SongRead, SongUpdate
from kiosk.services import songs as service

# Public router (consumed by the frontend).
router = APIRouter(prefix="/songs", tags=["songs"])

# Admin router.
admin_router = APIRouter(
    prefix="/admin/songs", tags=["admin:songs"], dependencies=[Depends(admin_guard)]
)


@router.get("", response_model=list[SongRead])
def search_songs(
    q: str = "", genre: str = "All", session: Session = Depends(get_session)
) -> list[SongRead]:
    songs = service.search_songs(session, query=q, genre=genre)
    return [SongRead.from_song(s) for s in songs]


def _to_admin(song) -> SongAdminRead:
    return SongAdminRead(
        id=song.id,
        name=song.name,
        artist=song.artist,
        genre=song.genre,
        duration_seconds=song.duration_seconds,
        color=song.color,
        is_active=song.is_active,
        tags=[t.name for t in song.tags],
    )


@admin_router.get("", response_model=list[SongAdminRead])
def list_songs(session: Session = Depends(get_session)) -> list[SongAdminRead]:
    return [_to_admin(s) for s in service.search_songs(session, genre="All")]


@admin_router.post("", response_model=SongAdminRead, status_code=201)
def create_song(
    data: SongCreate, session: Session = Depends(get_session)
) -> SongAdminRead:
    return _to_admin(service.create_song(session, data))


@admin_router.patch("/{song_id}", response_model=SongAdminRead)
def update_song(
    song_id: int, data: SongUpdate, session: Session = Depends(get_session)
) -> SongAdminRead:
    song = service.get_song(session, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return _to_admin(service.update_song(session, song, data))


@admin_router.delete("/{song_id}", status_code=204)
def delete_song(song_id: int, session: Session = Depends(get_session)) -> None:
    song = service.get_song(session, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    service.delete_song(session, song)
