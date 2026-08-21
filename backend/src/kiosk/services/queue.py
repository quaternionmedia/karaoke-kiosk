"""Queue management — admin-only walk-up enqueueing and ordering."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.enums import PerformanceStatus
from kiosk.events.bus import EventBus
from kiosk.events import signals
from kiosk.models.base import utcnow
from kiosk.models.performance import Performance
from kiosk.schemas.session import Singer
from kiosk.services import performers as performer_service
from kiosk.services.performances import _begin, PerformanceError


def list_queue(
    session: Session, event_id: int | None = None
) -> list[Performance]:
    """List all queued performances, ordered by position."""
    stmt = select(Performance).where(
        Performance.status == PerformanceStatus.QUEUED
    ).order_by(Performance.queue_position)
    
    if event_id is not None:
        stmt = stmt.where(Performance.event_id == event_id)
    
    return list(session.exec(stmt).all())


def enqueue(
    session: Session,
    bus: EventBus,
    song_id: int,
    singer: Singer,
    event_id: int | None = None,
    venue_id: int | None = None,
) -> Performance:
    """Enqueue a new performance (admin walk-up)."""
    from kiosk.models.song import Song

    song = session.get(Song, song_id)
    if song is None:
        raise PerformanceError("Unknown song", status_code=404)

    performer = performer_service.get_or_create_performer(
        session, name=singer.name, email=singer.email
    )

    # Find the next position (max position + 1)
    result = session.exec(
        select(Performance).where(Performance.status == PerformanceStatus.QUEUED).order_by(Performance.queue_position.desc())
    ).first()
    next_pos = (result.queue_position or 0) + 1 if result else 1

    performance = Performance(
        song_id=song_id,
        performer_id=performer.id,
        event_id=event_id,
        status=PerformanceStatus.QUEUED,
        queue_position=next_pos,
    )
    session.add(performance)
    session.commit()
    session.refresh(performance)

    bus.emit(
        signals.QUEUE_CHANGED,
        signals.QueueChanged(event_id=event_id),
    )
    return performance


def move(
    session: Session,
    bus: EventBus,
    performance_id: int,
    to_index: int,
) -> Performance:
    """Move a queued performance to a new position, reordering the list."""
    performance = session.get(Performance, performance_id)
    if performance is None:
        raise PerformanceError("Performance not found", status_code=404)
    
    if performance.status != PerformanceStatus.QUEUED:
        raise PerformanceError("Can only reorder queued performances", status_code=400)

    # Get all queued performances ordered by position
    queued = list_queue(session, event_id=performance.event_id)
    
    # Remove from its current position and insert at the new one
    queued.remove(performance)
    queued.insert(to_index, performance)
    
    # Renumber all positions
    # ponytail: O(n) renumber per move, fine for a bar queue; switch to fractional ranks past ~1k rows
    for i, perf in enumerate(queued, 1):
        perf.queue_position = i
        session.add(perf)
    
    session.commit()
    session.refresh(performance)

    bus.emit(
        signals.QUEUE_CHANGED,
        signals.QueueChanged(event_id=performance.event_id),
    )
    return performance


def remove(
    session: Session,
    bus: EventBus,
    performance_id: int,
) -> Performance:
    """Cancel a queued performance and remove it from the queue."""
    from kiosk.services.performances import cancel_performance

    performance = session.get(Performance, performance_id)
    if performance is None:
        raise PerformanceError("Performance not found", status_code=404)
    
    if performance.status != PerformanceStatus.QUEUED:
        raise PerformanceError("Can only remove queued performances", status_code=400)

    event_id = performance.event_id
    
    # Cancel it
    cancelled = cancel_performance(session, performance)

    # Renumber remaining queue
    queued = list_queue(session, event_id=event_id)
    for i, perf in enumerate(queued, 1):
        perf.queue_position = i
        session.add(perf)
    session.commit()

    bus.emit(
        signals.QUEUE_CHANGED,
        signals.QueueChanged(event_id=event_id),
    )
    return cancelled


def start_next(
    session: Session,
    bus: EventBus,
    event_id: int | None = None,
    venue_id: int | None = None,
) -> Performance:
    """Promote the next queued performance to PLAYING."""
    # Get the first queued performance
    stmt = select(Performance).where(
        Performance.status == PerformanceStatus.QUEUED
    ).order_by(Performance.queue_position)
    
    if event_id is not None:
        stmt = stmt.where(Performance.event_id == event_id)
    
    performance = session.exec(stmt).first()
    if performance is None:
        raise PerformanceError("No queued performance", status_code=404)

    # Begin playback (this calls _begin which handles status, recording, PERFORMANCE_STARTED)
    played = _begin(session, bus, performance, venue_id=venue_id)
    
    # Renumber remaining queue
    queued = list_queue(session, event_id=event_id)
    for i, perf in enumerate(queued, 1):
        perf.queue_position = i
        session.add(perf)
    session.commit()

    bus.emit(
        signals.QUEUE_CHANGED,
        signals.QueueChanged(event_id=event_id),
    )
    
    return played
