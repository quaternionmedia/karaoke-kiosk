"""Event CRUD plus activation."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.enums import EventStatus
from kiosk.models.event import Event
from kiosk.schemas.event import EventCreate, EventUpdate


def list_events(session: Session, venue_id: int | None = None) -> list[Event]:
    stmt = select(Event)
    if venue_id is not None:
        stmt = stmt.where(Event.venue_id == venue_id)
    return list(session.exec(stmt).all())


def get_event(session: Session, event_id: int) -> Event | None:
    return session.get(Event, event_id)


def get_active_event(session: Session, venue_id: int) -> Event | None:
    return session.exec(
        select(Event).where(
            Event.venue_id == venue_id, Event.status == EventStatus.ACTIVE
        )
    ).first()


def create_event(session: Session, data: EventCreate) -> Event:
    event = Event(**data.model_dump())
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def update_event(session: Session, event: Event, data: EventUpdate) -> Event:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def activate_event(session: Session, event: Event) -> Event:
    """Set this event ACTIVE and close any other active events at the venue."""
    siblings = session.exec(
        select(Event).where(
            Event.venue_id == event.venue_id,
            Event.status == EventStatus.ACTIVE,
            Event.id != event.id,
        )
    ).all()
    for sibling in siblings:
        sibling.status = EventStatus.CLOSED
        session.add(sibling)
    event.status = EventStatus.ACTIVE
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def delete_event(session: Session, event: Event) -> None:
    session.delete(event)
    session.commit()
