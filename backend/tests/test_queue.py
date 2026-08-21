"""Queue management tests."""

from __future__ import annotations

from kiosk.enums import PerformanceStatus


def test_enqueue_creates_queued_performance(client, songs, venue):
    """Enqueueing a song creates a QUEUED performance."""
    from kiosk.enums import PerformanceStatus
    
    created = client.post(
        "/api/admin/queue",
        json={"song_id": songs[0].id, "singer": {"name": "Alice", "email": "a@x.com"}},
    ).json()
    
    assert created["status"] == PerformanceStatus.QUEUED
    assert created["queue_position"] == 1
    assert created["performer_id"]


def test_list_queue_ordered(client, songs, venue):
    """Queue is ordered by position."""
    # Enqueue three singers
    for i, name in enumerate(["Alice", "Bob", "Carol"], 1):
        client.post(
            "/api/admin/queue",
            json={"song_id": songs[0].id, "singer": {"name": name, "email": f"{name.lower()}@x.com"}},
        )
    
    queue = client.get("/api/admin/queue").json()
    assert len(queue) == 3
    assert [p["queue_position"] for p in queue] == [1, 2, 3]


def test_move_reorders_queue(client, songs, venue):
    """Moving a performance reorders the rest."""
    # Enqueue three
    ids = []
    for i, name in enumerate(["Alice", "Bob", "Carol"], 1):
        resp = client.post(
            "/api/admin/queue",
            json={"song_id": songs[0].id, "singer": {"name": name, "email": f"{name.lower()}@x.com"}},
        ).json()
        ids.append(resp["id"])
    
    # Move Bob (id[1]) to position 0 (first)
    moved = client.post(f"/api/admin/queue/{ids[1]}/move", json={"to_index": 0}).json()
    assert moved["queue_position"] == 1
    
    # Check reordering
    queue = client.get("/api/admin/queue").json()
    assert queue[0]["id"] == ids[1]  # Bob is now first
    assert queue[1]["id"] == ids[0]  # Alice is now second
    assert queue[2]["id"] == ids[2]  # Carol is still third


def test_remove_from_queue(client, songs, venue):
    """Removing a queued performance cancels it."""
    # Enqueue two
    resp1 = client.post(
        "/api/admin/queue",
        json={"song_id": songs[0].id, "singer": {"name": "Alice", "email": "a@x.com"}},
    ).json()
    resp2 = client.post(
        "/api/admin/queue",
        json={"song_id": songs[0].id, "singer": {"name": "Bob", "email": "b@x.com"}},
    ).json()
    
    # Remove the first
    client.delete(f"/api/admin/queue/{resp1['id']}")
    
    # Check it's cancelled and queue renumbered
    queue = client.get("/api/admin/queue").json()
    assert len(queue) == 1
    assert queue[0]["id"] == resp2["id"]
    assert queue[0]["queue_position"] == 1


def test_start_next_plays_head(client, songs, venue, events_log, active_event):
    """start_next promotes the head to PLAYING and fires PERFORMANCE_STARTED."""
    # Enqueue two
    resp1 = client.post(
        "/api/admin/queue",
        json={
            "song_id": songs[0].id,
            "singer": {"name": "Alice", "email": "a@x.com"},
            "event_id": active_event.id,
        },
    ).json()
    resp2 = client.post(
        "/api/admin/queue",
        json={
            "song_id": songs[0].id,
            "singer": {"name": "Bob", "email": "b@x.com"},
            "event_id": active_event.id,
        },
    ).json()
    
    # Start next
    started = client.post("/api/admin/queue/start-next", params={"event_id": active_event.id}).json()
    
    assert started["status"] == PerformanceStatus.PLAYING
    assert started["queue_position"] is None
    assert started["id"] == resp1["id"]
    
    # Check PERFORMANCE_STARTED was fired
    assert any(name == "performance.started" for name, _ in events_log)
    
    # Check queue has only Bob left and he's position 1
    queue = client.get("/api/admin/queue").json()
    assert len(queue) == 1
    assert queue[0]["id"] == resp2["id"]
    assert queue[0]["queue_position"] == 1


def test_start_next_creates_recording(client, songs, active_event):
    """start_next creates a pending Recording for the performance."""
    client.post(
        "/api/admin/queue",
        json={
            "song_id": songs[0].id,
            "singer": {"name": "Alice", "email": "a@x.com"},
            "event_id": active_event.id,
        },
    )
    
    started = client.post("/api/admin/queue/start-next", params={"event_id": active_event.id}).json()
    
    # Fetch the performance and check it has a recording
    perf = client.get(f"/api/admin/performances/{started['id']}").json()
    assert perf["recording"]["id"]
    assert perf["recording"]["status"] == "pending"
