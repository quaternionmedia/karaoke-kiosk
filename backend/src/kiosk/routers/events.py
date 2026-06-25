"""Event admin endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard
from kiosk.schemas.event import EventCreate, EventRead, EventUpdate
from kiosk.services import events as service

admin_router = APIRouter(
    prefix="/admin/events", tags=["admin:events"], dependencies=[Depends(admin_guard)]
)


@admin_router.get("", response_model=list[EventRead])
def list_events(
    venue_id: int | None = None, session: Session = Depends(get_session)
) -> list[EventRead]:
    return service.list_events(session, venue_id=venue_id)


@admin_router.post("", response_model=EventRead, status_code=201)
def create_event(
    data: EventCreate, session: Session = Depends(get_session)
) -> EventRead:
    return service.create_event(session, data)


@admin_router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, session: Session = Depends(get_session)) -> EventRead:
    event = service.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@admin_router.patch("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int, data: EventUpdate, session: Session = Depends(get_session)
) -> EventRead:
    event = service.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return service.update_event(session, event, data)


@admin_router.post("/{event_id}/activate", response_model=EventRead)
def activate_event(
    event_id: int, session: Session = Depends(get_session)
) -> EventRead:
    event = service.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return service.activate_event(session, event)


@admin_router.delete("/{event_id}", status_code=204)
def delete_event(event_id: int, session: Session = Depends(get_session)) -> None:
    event = service.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    service.delete_event(session, event)
