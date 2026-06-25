"""Song model plus the Tag many-to-many for richer admin tagging."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.performance import Performance


class SongTagLink(TimestampMixin, table=True):
    """Association table linking songs and tags."""

    song_id: int | None = Field(default=None, foreign_key="song.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tag.id", primary_key=True)


class Tag(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    songs: list["Song"] = Relationship(back_populates="tags", link_model=SongTagLink)


class Song(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # DB canonical name; exposed to the frontend as ``title``.
    name: str = Field(index=True)
    artist: str = Field(index=True)
    # Single primary genre that the frontend filters and displays.
    genre: str | None = Field(default=None, index=True)
    # Stored as seconds; formatted to "M:SS" for the frontend.
    duration_seconds: int | None = None
    # Accent color (hex); defaulted from a genre map in the service layer.
    color: str | None = None
    is_active: bool = True

    performances: list["Performance"] = Relationship(back_populates="song")
    tags: list[Tag] = Relationship(back_populates="songs", link_model=SongTagLink)
