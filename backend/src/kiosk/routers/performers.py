"""Performer admin endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard
from kiosk.schemas.performer import PerformerRead, PerformerUpdate
from kiosk.services import performers as service

admin_router = APIRouter(
    prefix="/admin/performers",
    tags=["admin:performers"],
    dependencies=[Depends(admin_guard)],
)


@admin_router.get("", response_model=list[PerformerRead])
def list_performers(
    email: str | None = None, session: Session = Depends(get_session)
) -> list[PerformerRead]:
    return service.list_performers(session, email=email)


@admin_router.get("/{performer_id}", response_model=PerformerRead)
def get_performer(
    performer_id: int, session: Session = Depends(get_session)
) -> PerformerRead:
    performer = service.get_performer(session, performer_id)
    if performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    return performer


@admin_router.patch("/{performer_id}", response_model=PerformerRead)
def update_performer(
    performer_id: int,
    data: PerformerUpdate,
    session: Session = Depends(get_session),
) -> PerformerRead:
    performer = service.get_performer(session, performer_id)
    if performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    return service.update_performer(session, performer, data)


@admin_router.delete("/{performer_id}", status_code=204)
def delete_performer(
    performer_id: int, session: Session = Depends(get_session)
) -> None:
    performer = service.get_performer(session, performer_id)
    if performer is None:
        raise HTTPException(status_code=404, detail="Performer not found")
    service.delete_performer(session, performer)
