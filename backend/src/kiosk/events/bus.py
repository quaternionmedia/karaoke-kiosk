"""A tiny synchronous publish/subscribe event bus.

Handlers are isolated: an exception in one handler is logged and swallowed so a
failing integration (e.g. an unreachable OBS instance) never breaks the HTTP
request that triggered the event.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("kiosk.events")

Handler = Callable[[Any], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str, payload: Any) -> None:
        for handler in self._handlers.get(event_name, []):
            try:
                handler(payload)
            except Exception:  # noqa: BLE001 - handlers must never break the caller
                logger.exception(
                    "Handler %r failed for event %s", handler, event_name
                )

    def handlers_for(self, event_name: str) -> list[Handler]:
        return list(self._handlers.get(event_name, []))
