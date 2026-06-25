"""In-process event/hook system for kiosk lifecycle triggers."""

from kiosk.events.bus import EventBus
from kiosk.events.handlers import register_default_handlers

__all__ = ["EventBus", "register_default_handlers"]
