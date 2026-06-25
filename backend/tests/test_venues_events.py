"""Admin CRUD tests for venues, events, and performers."""

from __future__ import annotations

from kiosk.enums import EventStatus


def test_venue_crud_and_public_config(client):
    created = client.post(
        "/api/admin/venues",
        json={"name": "Star Bar", "welcome_message": "Sing!", "countdown_from": 5},
    )
    assert created.status_code == 201
    venue_id = created.json()["id"]

    # Public kiosk config endpoint maps fields for the frontend.
    cfg = client.get("/api/venue").json()
    assert cfg["venue_name"] == "Star Bar"
    assert cfg["countdown_from"] == 5

    patched = client.patch(
        f"/api/admin/venues/{venue_id}", json={"location": "Downtown"}
    )
    assert patched.json()["location"] == "Downtown"

    assert client.delete(f"/api/admin/venues/{venue_id}").status_code == 204
    assert client.get("/api/venue").status_code == 404


def test_venue_create_validation_422(client):
    assert client.post("/api/admin/venues", json={}).status_code == 422


def test_event_activate_closes_siblings(client, venue):
    def make_event(name):
        return client.post(
            "/api/admin/events",
            json={
                "venue_id": venue.id,
                "name": name,
                "starts_at": "2026-06-24T20:00:00Z",
            },
        ).json()

    first = make_event("First")
    second = make_event("Second")

    client.post(f"/api/admin/events/{first['id']}/activate")
    client.post(f"/api/admin/events/{second['id']}/activate")

    events = {e["id"]: e for e in client.get("/api/admin/events").json()}
    assert events[first["id"]]["status"] == EventStatus.CLOSED
    assert events[second["id"]]["status"] == EventStatus.ACTIVE


def test_performer_listing_after_session(client, songs, venue):
    client.post(
        "/api/session/start",
        json={"songId": songs[0].id, "singer": {"name": "Cara", "email": "c@x.com"}},
    )
    found = client.get("/api/admin/performers", params={"email": "c@x.com"}).json()
    assert len(found) == 1
    assert found[0]["name"] == "Cara"
