"""Performer CRUD and get-or-create."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.models.performer import Performer
from kiosk.schemas.performer import PerformerUpdate


def list_performers(session: Session, email: str | None = None) -> list[Performer]:
    stmt = select(Performer)
    if email:
        stmt = stmt.where(Performer.email == email)
    return list(session.exec(stmt).all())


def get_performer(session: Session, performer_id: int) -> Performer | None:
    return session.get(Performer, performer_id)


def get_or_create_performer(
    session: Session, name: str, email: str
) -> Performer:
    """Reuse an existing performer by email; otherwise create one.

    Performers with no email (anonymous) always get a fresh row.
    """
    if email:
        existing = session.exec(
            select(Performer).where(Performer.email == email)
        ).first()
        if existing is not None:
            if name and existing.name != name:
                existing.name = name
                session.add(existing)
            return existing
    performer = Performer(name=name, email=email)
    session.add(performer)
    session.commit()
    session.refresh(performer)
    return performer


def update_performer(
    session: Session, performer: Performer, data: PerformerUpdate
) -> Performer:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(performer, key, value)
    session.add(performer)
    session.commit()
    session.refresh(performer)
    return performer


def delete_performer(session: Session, performer: Performer) -> None:
    session.delete(performer)
    session.commit()
