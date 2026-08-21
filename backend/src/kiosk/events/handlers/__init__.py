"""Default handler registration."""

from __future__ import annotations

from kiosk.config import Settings
from kiosk.events.bus import EventBus
from kiosk.events.handlers import email, obs, ws
from kiosk.events.signals import (
    EMAIL_SEND,
    PERFORMANCE_FINISHED,
    PERFORMANCE_STARTED,
    QUEUE_CHANGED,
)


def register_default_handlers(bus: EventBus, settings: Settings) -> None:
    """Subscribe the built-in OBS, email, and WebSocket handlers.

    Tests skip this and subscribe their own spy handlers instead.
    """
    obs_handler = obs.ObsHandler(settings)
    bus.subscribe(PERFORMANCE_STARTED, obs_handler.on_performance_started)
    bus.subscribe(PERFORMANCE_FINISHED, obs_handler.on_performance_finished)

    email_handler = email.EmailHandler(settings)
    bus.subscribe(EMAIL_SEND, email_handler.on_email_send)

    broadcaster = ws.get_broadcaster()
    bus.subscribe(QUEUE_CHANGED, broadcaster.on_queue_changed)


__all__ = ["register_default_handlers"]
