"""Performance admin DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from kiosk.enums import PerformanceStatus, RecordingStatus


class RecordingRead(BaseModel):
    id: int
    status: RecordingStatus
    url: str | None
    shared_at: datetime | None

    model_config = {"from_attributes": True}


class PerformanceRead(BaseModel):
    id: int
    session_token: str
    event_id: int | None
    performer_id: int
    song_id: int
    status: PerformanceStatus
    queue_position: int | None
    started_at: datetime | None
    finished_at: datetime | None
    recording: RecordingRead | None = None

    model_config = {"from_attributes": True}
