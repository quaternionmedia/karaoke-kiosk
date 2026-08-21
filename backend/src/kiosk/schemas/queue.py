"""Queue operation request DTOs."""

from __future__ import annotations

from pydantic import BaseModel

from kiosk.schemas.session import Singer


class QueueEnqueueRequest(BaseModel):
    song_id: int
    singer: Singer
    event_id: int | None = None


class QueueMoveRequest(BaseModel):
    to_index: int
