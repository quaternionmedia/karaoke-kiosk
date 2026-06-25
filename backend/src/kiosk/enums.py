"""Status enumerations shared across models and schemas.

All enums subclass ``str`` so they serialize as plain strings in JSON, which
keeps values like ``"playing"`` / ``"finished"`` aligned with the frontend.
"""

from __future__ import annotations

from enum import Enum


class PerformanceStatus(str, Enum):
    QUEUED = "queued"
    PLAYING = "playing"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class RecordingStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    SHARED = "shared"
    FAILED = "failed"


class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    CLOSED = "closed"
