"""WebSocket queue update tests."""

from __future__ import annotations

import json


def test_queue_ws_connect_accept(client):
    """WebSocket can connect to /api/admin/queue/ws."""
    with client.websocket_connect("/api/admin/queue/ws") as ws:
        # Should connect without error
        assert ws


def test_queue_ws_receives_nudge_on_enqueue(client, songs, venue, session):
    """WebSocket receives a nudge when a performance is enqueued."""
    with client.websocket_connect("/api/admin/queue/ws") as ws:
        # Enqueue a performance
        client.post(
            "/api/admin/queue",
            json={"song_id": songs[0].id, "singer": {"name": "Alice", "email": "a@x.com"}},
        )
        
        # Receive the nudge
        msg = ws.receive_json()
        assert msg["type"] == "queue.changed"


def test_queue_ws_receives_nudge_on_start_next(client, songs, venue, active_event):
    """WebSocket receives a nudge when start-next is called."""
    with client.websocket_connect("/api/admin/queue/ws") as ws:
        # Enqueue and start
        client.post(
            "/api/admin/queue",
            json={
                "song_id": songs[0].id,
                "singer": {"name": "Alice", "email": "a@x.com"},
                "event_id": active_event.id,
            },
        )
        ws.receive_json()  # consume enqueue nudge
        
        client.post("/api/admin/queue/start-next", params={"event_id": active_event.id})
        
        msg = ws.receive_json()
        assert msg["type"] == "queue.changed"
