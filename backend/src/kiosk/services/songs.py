"""Song CRUD and search."""

from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, or_, select

from kiosk.models.song import Song, Tag
from kiosk.schemas.song import SongCreate, SongUpdate
from kiosk.utils import color_for_genre


def _get_or_create_tags(session: Session, names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    for name in names:
        tag = session.exec(select(Tag).where(Tag.name == name)).first()
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
        tags.append(tag)
    return tags


def search_songs(
    session: Session, query: str = "", genre: str = "All"
) -> list[Song]:
    """Search active songs by free text and genre (``"All"`` = no filter)."""
    stmt = select(Song).where(Song.is_active == True)  # noqa: E712
    if genre and genre != "All":
        stmt = stmt.where(Song.genre == genre)
    if query:
        like = f"%{query.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Song.name).like(like),
                func.lower(Song.artist).like(like),
            )
        )
    return list(session.exec(stmt).all())


def get_song(session: Session, song_id: int) -> Song | None:
    return session.get(Song, song_id)


def create_song(session: Session, data: SongCreate) -> Song:
    song = Song(
        name=data.name,
        artist=data.artist,
        genre=data.genre,
        duration_seconds=data.duration_seconds,
        color=data.color or color_for_genre(data.genre),
        is_active=data.is_active,
    )
    song.tags = _get_or_create_tags(session, data.tags)
    session.add(song)
    session.commit()
    session.refresh(song)
    return song


def update_song(session: Session, song: Song, data: SongUpdate) -> Song:
    fields = data.model_dump(exclude_unset=True, exclude={"tags"})
    for key, value in fields.items():
        setattr(song, key, value)
    if data.tags is not None:
        song.tags = _get_or_create_tags(session, data.tags)
    session.add(song)
    session.commit()
    session.refresh(song)
    return song


def delete_song(session: Session, song: Song) -> None:
    session.delete(song)
    session.commit()
