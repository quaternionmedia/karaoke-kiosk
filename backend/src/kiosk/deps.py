"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request, status

from kiosk.config import Settings, get_settings
from kiosk.events.bus import EventBus


def get_bus(request: Request) -> EventBus:
    """Return the application's event bus (stored on ``app.state``)."""
    return request.app.state.bus


def admin_guard(
    x_admin_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Shared-secret guard for admin routes.

    Disabled (no-op) unless ``settings.admin_api_key`` is configured.
    """
    if settings.admin_api_key is None:
        return
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key"
        )
