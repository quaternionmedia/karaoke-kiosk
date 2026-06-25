"""Performance admin (read + cancel) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard
from kiosk.enums import PerformanceStatus
from kiosk.schemas.performance import PerformanceRead
from kiosk.services import performances as service

admin_router = APIRouter(
    prefix="/admin/performances",
    tags=["admin:performances"],
    dependencies=[Depends(admin_guard)],
)


@admin_router.get("", response_model=list[PerformanceRead])
def list_performances(
    event_id: int | None = None,
    performer_id: int | None = None,
    status: PerformanceStatus | None = None,
    session: Session = Depends(get_session),
) -> list[PerformanceRead]:
    return service.list_performances(
        session, event_id=event_id, performer_id=performer_id, status=status
    )


@admin_router.get("/{performance_id}", response_model=PerformanceRead)
def get_performance(
    performance_id: int, session: Session = Depends(get_session)
) -> PerformanceRead:
    from kiosk.models.performance import Performance

    performance = session.get(Performance, performance_id)
    if performance is None:
        raise HTTPException(status_code=404, detail="Performance not found")
    return performance


@admin_router.post("/{performance_id}/cancel", response_model=PerformanceRead)
def cancel_performance(
    performance_id: int, session: Session = Depends(get_session)
) -> PerformanceRead:
    from kiosk.models.performance import Performance

    performance = session.get(Performance, performance_id)
    if performance is None:
        raise HTTPException(status_code=404, detail="Performance not found")
    return service.cancel_performance(session, performance)
