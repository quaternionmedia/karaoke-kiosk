"""Venue DTOs."""

from __future__ import annotations

from pydantic import BaseModel

from kiosk.models.venue import Venue


class VenueCreate(BaseModel):
    name: str
    location: str | None = None
    welcome_message: str | None = None
    splash_delay_ms: int = 3500
    countdown_from: int = 3
    thank_you_duration_ms: int = 5000
    obs_ws_url: str | None = None
    obs_ws_password: str | None = None
    is_active: bool = True


class VenueUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    welcome_message: str | None = None
    splash_delay_ms: int | None = None
    countdown_from: int | None = None
    thank_you_duration_ms: int | None = None
    obs_ws_url: str | None = None
    obs_ws_password: str | None = None
    is_active: bool | None = None


class VenueRead(BaseModel):
    id: int
    name: str
    location: str | None
    welcome_message: str | None
    splash_delay_ms: int
    countdown_from: int
    thank_you_duration_ms: int
    is_active: bool

    model_config = {"from_attributes": True}


class VenueConfig(BaseModel):
    """Public kiosk config (lets the frontend drop its hardcoded config.ts)."""

    id: int
    venue_name: str
    venue_message: str | None
    splash_delay: int
    countdown_from: int
    thank_you_duration: int

    @classmethod
    def from_venue(cls, venue: Venue) -> "VenueConfig":
        return cls(
            id=venue.id,
            venue_name=venue.name,
            venue_message=venue.welcome_message,
            splash_delay=venue.splash_delay_ms,
            countdown_from=venue.countdown_from,
            thank_you_duration=venue.thank_you_duration_ms,
        )
