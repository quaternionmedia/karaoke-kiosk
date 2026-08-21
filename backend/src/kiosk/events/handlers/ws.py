"""WebSocket broadcaster for queue updates."""

from __future__ import annotations

import asyncio
import logging
from asyncio import AbstractEventLoop

from kiosk.events.signals import QueueChanged

logger = logging.getLogger("kiosk.events.ws")


class QueueBroadcaster:
    """Broadcast queue changes to connected WebSocket clients.
    
    Routes async broadcasts from a sync event bus by capturing the running
    event loop and using call_soon_threadsafe to post messages to client queues.
    """
    
    def __init__(self) -> None:
        self.loop: AbstractEventLoop | None = None
        self.clients: set[asyncio.Queue[dict]] = set()
    
    def set_loop(self, loop: AbstractEventLoop) -> None:
        """Capture the running event loop (called from lifespan)."""
        self.loop = loop
    
    def subscribe_client(self, client_queue: asyncio.Queue[dict]) -> None:
        """Register a connected client's message queue."""
        self.clients.add(client_queue)
    
    def unsubscribe_client(self, client_queue: asyncio.Queue[dict]) -> None:
        """Unregister a client."""
        self.clients.discard(client_queue)
    
    def on_queue_changed(self, payload: QueueChanged) -> None:
        """Broadcast a queue.changed nudge to all connected clients."""
        if not self.loop or not self.clients:
            return
        
        msg = {"type": "queue.changed", "event_id": payload.event_id}
        
        # Schedule the broadcast in the event loop (from a sync handler context)
        def broadcast():
            dead = []
            for q in self.clients:
                try:
                    q.put_nowait(msg)
                except asyncio.QueueFull:
                    logger.warning("Client queue full; dropping message")
                    dead.append(q)
            for q in dead:
                self.clients.discard(q)
        
        self.loop.call_soon_threadsafe(broadcast)


# Singleton broadcaster instance
_broadcaster = QueueBroadcaster()


def get_broadcaster() -> QueueBroadcaster:
    """Return the singleton broadcaster."""
    return _broadcaster
