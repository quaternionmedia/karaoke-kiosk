"""Song search + admin CRUD tests."""

from __future__ import annotations


def test_search_returns_frontend_shape(client, songs):
    resp = client.get("/api/songs")
    assert resp.status_code == 200
    body = resp.json()
    # Inactive song hidden.
    assert len(body) == 2
    item = next(s for s in body if s["title"] == "Bohemian Rhapsody")
    assert set(item) == {"id", "title", "artist", "genre", "duration", "color"}
    assert item["duration"] == "5:55"
    assert item["color"] == "#f59e0b"


def test_genre_filter(client, songs):
    rock = client.get("/api/songs", params={"genre": "Rock"}).json()
    assert [s["title"] for s in rock] == ["Bohemian Rhapsody"]

    all_songs = client.get("/api/songs", params={"genre": "All"}).json()
    assert len(all_songs) == 2


def test_query_is_case_insensitive_on_title_and_artist(client, songs):
    by_artist = client.get("/api/songs", params={"q": "queen"}).json()
    assert [s["title"] for s in by_artist] == ["Bohemian Rhapsody"]

    by_title = client.get("/api/songs", params={"q": "caroline"}).json()
    assert [s["title"] for s in by_title] == ["Sweet Caroline"]


def test_admin_create_defaults_color_from_genre(client):
    resp = client.post(
        "/api/admin/songs",
        json={"name": "Mr. Brightside", "artist": "The Killers", "genre": "Rock",
              "duration_seconds": 222, "tags": ["anthem", "2000s"]},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["color"] == "#f59e0b"  # default Rock color
    assert sorted(body["tags"]) == ["2000s", "anthem"]

    # Visible in public search with formatted duration.
    found = client.get("/api/songs", params={"q": "brightside"}).json()
    assert found[0]["duration"] == "3:42"
