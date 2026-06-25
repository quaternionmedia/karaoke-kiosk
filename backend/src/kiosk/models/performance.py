"""Performance model — one karaoke performance (the frontend "session")."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlmodel import Field, Relationship

from kiosk.enums import PerformanceStatus
from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.event import Event
    from kiosk.models.performer import Performer
    from kiosk.models.recording import Recording
    from kiosk.models.song import Song


def _new_token() -> str:
    return uuid4().hex


class Performance(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Opaque token returned to the frontend as ``sessionId`` (not the PK).
    session_token: str = Field(default_factory=_new_token, unique=True, index=True)

    # Nullable so a standalone kiosk works without an active event.
    event_id: int | None = Field(default=None, foreign_key="event.id", index=True)
    performer_id: int = Field(foreign_key="performer.id", index=True)
    song_id: int = Field(foreign_key="song.id", index=True)

    status: PerformanceStatus = Field(default=PerformanceStatus.PLAYING, index=True)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    event: Optional["Event"] = Relationship(back_populates="performances")
    performer: "Performer" = Relationship(back_populates="performances")
    song: "Song" = Relationship(back_populates="performances")
    recording: Optional["Recording"] = Relationship(
        back_populates="performance",
        sa_relationship_kwargs={"uselist": False},
    )
