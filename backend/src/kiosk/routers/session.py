"""Session lifecycle endpoints (frontend contract)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import get_bus
from kiosk.events.bus import EventBus
from kiosk.schemas.session import (
    SessionStartRequest,
    SessionStartResponse,
    StopResponse,
)
from kiosk.services import performances as service
from kiosk.services import venues as venue_service

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start", response_model=SessionStartResponse)
def start(
    payload: SessionStartRequest,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> SessionStartResponse:
    # Auto-attach to the default venue's active event when one exists.
    venue = venue_service.get_default_venue(session)
    venue_id = venue.id if venue else None
    try:
        performance = service.start_performance(
            session, bus, payload.song_id, payload.singer, venue_id=venue_id
        )
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return SessionStartResponse(session_id=performance.session_token, status="playing")


@router.post("/{session_id}/stop", response_model=StopResponse)
def stop(
    session_id: str,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> StopResponse:
    try:
        _, recording = service.stop_performance(session, bus, session_id)
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return StopResponse(
        recording_url=recording.url if recording else None, status="finished"
    )
