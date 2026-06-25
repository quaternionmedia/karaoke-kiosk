"""Venue CRUD."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.models.venue import Venue
from kiosk.schemas.venue import VenueCreate, VenueUpdate


def list_venues(session: Session) -> list[Venue]:
    return list(session.exec(select(Venue)).all())


def get_venue(session: Session, venue_id: int) -> Venue | None:
    return session.get(Venue, venue_id)


def get_default_venue(session: Session) -> Venue | None:
    """Return the first active venue (used for the public kiosk config)."""
    return session.exec(
        select(Venue).where(Venue.is_active == True).order_by(Venue.id)  # noqa: E712
    ).first()


def create_venue(session: Session, data: VenueCreate) -> Venue:
    venue = Venue(**data.model_dump())
    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


def update_venue(session: Session, venue: Venue, data: VenueUpdate) -> Venue:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(venue, key, value)
    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


def delete_venue(session: Session, venue: Venue) -> None:
    session.delete(venue)
    session.commit()
