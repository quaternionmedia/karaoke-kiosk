"""Performance lifecycle: start, stop, share. Fires lifecycle hooks."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.enums import PerformanceStatus, RecordingStatus
from kiosk.events.bus import EventBus
from kiosk.events import signals
from kiosk.models.base import utcnow
from kiosk.models.performance import Performance
from kiosk.models.recording import Recording
from kiosk.schemas.session import Singer
from kiosk.services import events as event_service
from kiosk.services import performers as performer_service


class PerformanceError(Exception):
    """Raised when a lifecycle operation cannot proceed (maps to HTTP 4xx)."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_by_token(session: Session, token: str) -> Performance | None:
    return session.exec(
        select(Performance).where(Performance.session_token == token)
    ).first()


def list_performances(
    session: Session,
    event_id: int | None = None,
    performer_id: int | None = None,
    status: PerformanceStatus | None = None,
) -> list[Performance]:
    stmt = select(Performance)
    if event_id is not None:
        stmt = stmt.where(Performance.event_id == event_id)
    if performer_id is not None:
        stmt = stmt.where(Performance.performer_id == performer_id)
    if status is not None:
        stmt = stmt.where(Performance.status == status)
    return list(session.exec(stmt).all())


def start_performance(
    session: Session,
    bus: EventBus,
    song_id: int,
    singer: Singer,
    venue_id: int | None = None,
) -> Performance:
    """Begin a performance and emit ``performance.started``.

    Resolves the song, gets-or-creates the performer, auto-attaches the venue's
    active event when available, and creates a pending Recording.
    """
    from kiosk.models.song import Song  # local import to avoid cycles

    song = session.get(Song, song_id)
    if song is None:
        raise PerformanceError("Unknown song", status_code=404)

    performer = performer_service.get_or_create_performer(
        session, name=singer.name, email=singer.email
    )

    event_id = None
    if venue_id is not None:
        active = event_service.get_active_event(session, venue_id)
        event_id = active.id if active else None

    performance = Performance(
        song_id=song_id,
        performer_id=performer.id,
        event_id=event_id,
        status=PerformanceStatus.PLAYING,
        started_at=utcnow(),
    )
    session.add(performance)
    session.commit()
    session.refresh(performance)

    recording = Recording(
        performance_id=performance.id, status=RecordingStatus.PENDING
    )
    session.add(recording)
    session.commit()

    bus.emit(
        signals.PERFORMANCE_STARTED,
        signals.PerformanceStarted(
            performance_id=performance.id,
            session_token=performance.session_token,
            song_id=song_id,
            performer_id=performer.id,
            venue_id=venue_id,
            event_id=event_id,
        ),
    )
    return performance


def stop_performance(
    session: Session, bus: EventBus, token: str
) -> tuple[Performance, Recording | None]:
    """Finish a performance and emit ``performance.finished``."""
    performance = get_by_token(session, token)
    if performance is None:
        raise PerformanceError("Unknown session", status_code=404)

    performance.status = PerformanceStatus.FINISHED
    performance.finished_at = utcnow()
    session.add(performance)
    session.commit()
    session.refresh(performance)

    recording = session.exec(
        select(Recording).where(Recording.performance_id == performance.id)
    ).first()

    bus.emit(
        signals.PERFORMANCE_FINISHED,
        signals.PerformanceFinished(
            performance_id=performance.id,
            session_token=performance.session_token,
            recording_id=recording.id if recording else None,
        ),
    )
    return performance, recording


def share_recording(
    session: Session, bus: EventBus, token: str, email: str
) -> Recording:
    """Mark a recording shared and emit ``recording.ready`` + ``email.send``."""
    performance = get_by_token(session, token)
    if performance is None:
        raise PerformanceError("Unknown session", status_code=404)

    recording = session.exec(
        select(Recording).where(Recording.performance_id == performance.id)
    ).first()
    if recording is None:
        recording = Recording(performance_id=performance.id)

    recording.shared_at = utcnow()
    if recording.status != RecordingStatus.READY:
        recording.status = RecordingStatus.SHARED
    session.add(recording)
    session.commit()
    session.refresh(recording)

    bus.emit(
        signals.RECORDING_READY,
        signals.RecordingReady(
            recording_id=recording.id,
            performance_id=performance.id,
            url=recording.url,
        ),
    )
    bus.emit(
        signals.EMAIL_SEND,
        _build_share_email(session, performance, recording, email),
    )
    return recording


def cancel_performance(session: Session, performance: Performance) -> Performance:
    performance.status = PerformanceStatus.CANCELLED
    performance.finished_at = utcnow()
    session.add(performance)
    session.commit()
    session.refresh(performance)
    return performance


def _build_share_email(
    session: Session,
    performance: Performance,
    recording: Recording,
    email: str,
) -> signals.EmailSend:
    """Render the recording-share email from the venue's templates."""
    from kiosk.models.song import Song
    from kiosk.models.venue import Venue

    song = session.get(Song, performance.song_id)
    venue: Venue | None = None
    if performance.event_id is not None:
        event = event_service.get_event(session, performance.event_id)
        if event is not None:
            venue = session.get(Venue, event.venue_id)

    venue_name = venue.name if venue else "Karaoke Kiosk"
    subject_tpl = (
        venue.email_subject_template
        if venue and venue.email_subject_template
        else "Your performance at {venue}!"
    )
    body_tpl = (
        venue.email_body_template
        if venue and venue.email_body_template
        else "Hi {name}, here is your recording of {song}: {recording_url}"
    )
    ctx = {
        "name": performance.performer.name if performance.performer else "",
        "song": song.name if song else "",
        "recording_url": recording.url or "",
        "venue": venue_name,
    }
    return signals.EmailSend(
        to=email,
        subject=subject_tpl.format(**ctx),
        body=body_tpl.format(**ctx),
        performance_id=performance.id,
    )
