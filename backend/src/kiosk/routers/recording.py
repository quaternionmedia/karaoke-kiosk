"""Recording share endpoint (frontend contract)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import get_bus
from kiosk.events.bus import EventBus
from kiosk.schemas.session import ShareRequest
from kiosk.services import performances as service

router = APIRouter(prefix="/recording", tags=["recording"])


@router.post("/share", status_code=204, response_class=Response)
def share(
    payload: ShareRequest,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> Response:
    try:
        service.share_recording(session, bus, payload.session_id, payload.email)
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return Response(status_code=204)
