"""Event names and their payloads.

Payloads carry only identifiers and primitive data (never ORM objects) so a
handler can run safely after the originating request/session has closed.
"""

from __future__ import annotations

from dataclasses import dataclass

# Event name constants.
PERFORMANCE_STARTED = "performance.started"
PERFORMANCE_FINISHED = "performance.finished"
RECORDING_READY = "recording.ready"
EMAIL_SEND = "email.send"
QUEUE_CHANGED = "queue.changed"


@dataclass(frozen=True)
class PerformanceStarted:
    performance_id: int
    session_token: str
    song_id: int
    performer_id: int
    venue_id: int | None
    event_id: int | None


@dataclass(frozen=True)
class PerformanceFinished:
    performance_id: int
    session_token: str
    recording_id: int | None


@dataclass(frozen=True)
class RecordingReady:
    recording_id: int
    performance_id: int
    url: str | None


@dataclass(frozen=True)
class EmailSend:
    to: str
    subject: str
    body: str
    performance_id: int | None = None


@dataclass(frozen=True)
class QueueChanged:
    event_id: int | None = None  # which event's queue changed, or None for all
