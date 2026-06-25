"""Event DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from kiosk.enums import EventStatus


class EventCreate(BaseModel):
    venue_id: int
    name: str
    starts_at: datetime
    ends_at: datetime | None = None
    status: EventStatus = EventStatus.SCHEDULED


class EventUpdate(BaseModel):
    name: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: EventStatus | None = None


class EventRead(BaseModel):
    id: int
    venue_id: int
    name: str
    starts_at: datetime
    ends_at: datetime | None
    status: EventStatus

    model_config = {"from_attributes": True}
