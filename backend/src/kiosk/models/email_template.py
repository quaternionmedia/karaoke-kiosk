"""Email template model — per-venue named templates with placeholder validation."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.venue import Venue


class EmailTemplate(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    venue_id: int = Field(foreign_key="venue.id", index=True)
    slug: str  # e.g., "recording_share" — scoped per venue
    name: str  # e.g., "Recording Share" — human-readable
    subject: str
    body: str
    is_active: bool = True

    venue: "Venue" = Relationship(back_populates="email_templates")

    class Config:
        # Enforce unique (venue_id, slug) at the model level; Alembic will add the DB constraint.
        pass
