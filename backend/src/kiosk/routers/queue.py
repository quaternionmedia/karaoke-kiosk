"""Admin queue management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard, get_bus
from kiosk.events.bus import EventBus
from kiosk.events.handlers.ws import get_broadcaster
from kiosk.schemas.performance import PerformanceRead
from kiosk.schemas.queue import QueueEnqueueRequest, QueueMoveRequest
from kiosk.services import queue as service
import asyncio

admin_router = APIRouter(
    prefix="/admin/queue",
    tags=["admin:queue"],
    dependencies=[Depends(admin_guard)],
)


@admin_router.get("", response_model=list[PerformanceRead])
def list_queue(
    event_id: int | None = None,
    session: Session = Depends(get_session),
) -> list[PerformanceRead]:
    """Get the current queue, ordered by position."""
    return service.list_queue(session, event_id=event_id)


@admin_router.post("", response_model=PerformanceRead, status_code=201)
def enqueue(
    data: QueueEnqueueRequest,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> PerformanceRead:
    """Enqueue a new performance (admin walk-up)."""
    try:
        return service.enqueue(
            session,
            bus,
            data.song_id,
            data.singer,
            event_id=data.event_id,
        )
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@admin_router.post("/{performance_id}/move", response_model=PerformanceRead)
def move(
    performance_id: int,
    data: QueueMoveRequest,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> PerformanceRead:
    """Reorder a queued performance to a new position."""
    try:
        return service.move(session, bus, performance_id, data.to_index)
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@admin_router.delete("/{performance_id}")
def remove(
    performance_id: int,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> dict:
    """Remove a queued performance."""
    try:
        service.remove(session, bus, performance_id)
        return {"status": "removed"}
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@admin_router.post("/start-next", response_model=PerformanceRead)
def start_next(
    event_id: int | None = None,
    session: Session = Depends(get_session),
    bus: EventBus = Depends(get_bus),
) -> PerformanceRead:
    """Promote the next queued performance to PLAYING."""
    try:
        return service.start_next(session, bus, event_id=event_id)
    except service.PerformanceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@admin_router.websocket("/ws")
async def queue_ws(websocket: WebSocket) -> None:
    """WebSocket connection for realtime queue updates.
    
    ponytail: WS unauthenticated; browsers can't set X-Admin-Key — move to a
    query-param or subprotocol token when ADMIN_API_KEY is enabled.
    """
    await websocket.accept()
    
    broadcaster = get_broadcaster()
    client_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=10)
    broadcaster.subscribe_client(client_queue)
    
    try:
        while True:
            # Wait for a message from the broadcaster
            msg = await client_queue.get()
            await websocket.send_json(msg)
    except WebSocketDisconnect:
        broadcaster.unsubscribe_client(client_queue)
    except Exception:
        broadcaster.unsubscribe_client(client_queue)
        raise
