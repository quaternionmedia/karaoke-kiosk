"""Event model — a karaoke night at a venue."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from kiosk.enums import EventStatus
from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.performance import Performance
    from kiosk.models.venue import Venue


class Event(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    venue_id: int = Field(foreign_key="venue.id", index=True)
    name: str
    starts_at: datetime
    ends_at: datetime | None = None
    status: EventStatus = Field(default=EventStatus.SCHEDULED, index=True)

    venue: "Venue" = Relationship(back_populates="events")
    performances: list["Performance"] = Relationship(back_populates="event")
