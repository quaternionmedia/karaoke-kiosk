"""Aggregate all routers under the ``/api`` prefix."""

from __future__ import annotations

from fastapi import APIRouter

from kiosk.routers import (
    events,
    performances,
    performers,
    recording,
    session,
    songs,
    venues,
)

api_router = APIRouter(prefix="/api")

# Public / frontend-facing.
api_router.include_router(songs.router)
api_router.include_router(session.router)
api_router.include_router(recording.router)
api_router.include_router(venues.router)

# Admin CRUD.
api_router.include_router(songs.admin_router)
api_router.include_router(venues.admin_router)
api_router.include_router(events.admin_router)
api_router.include_router(performers.admin_router)
api_router.include_router(performances.admin_router)

__all__ = ["api_router"]
