"""Venue model — per-location kiosk configuration."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.event import Event


class Venue(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    location: str | None = None
    welcome_message: str | None = None

    # Email templates support {name}, {song}, {recording_url}, {venue} placeholders.
    email_subject_template: str | None = None
    email_body_template: str | None = None

    # Kiosk UI timings (mirror frontend/src/config.ts).
    splash_delay_ms: int = 3500
    countdown_from: int = 3
    thank_you_duration_ms: int = 5000

    # Optional per-venue OBS connection (overrides global settings when set).
    obs_ws_url: str | None = None
    obs_ws_password: str | None = None

    is_active: bool = True

    events: list["Event"] = Relationship(back_populates="venue")
