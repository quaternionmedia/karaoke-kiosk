"""Session start/stop lifecycle tests (frontend contract)."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.enums import PerformanceStatus
from kiosk.models.performance import Performance
from kiosk.models.performer import Performer


def _start(client, song_id, name="Alice", email="alice@example.com"):
    return client.post(
        "/api/session/start",
        json={"songId": song_id, "singer": {"name": name, "email": email}},
    )


def test_start_returns_playing_and_token(client, engine, songs, venue, events_log):
    resp = _start(client, songs[0].id)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "playing"
    assert isinstance(body["sessionId"], str) and body["sessionId"]

    with Session(engine) as s:
        perf = s.exec(
            select(Performance).where(
                Performance.session_token == body["sessionId"]
            )
        ).one()
        assert perf.status == PerformanceStatus.PLAYING
        assert perf.started_at is not None

    assert any(name == "performance.started" for name, _ in events_log)


def test_start_autoattaches_active_event(client, engine, songs, active_event):
    resp = _start(client, songs[0].id)
    token = resp.json()["sessionId"]
    with Session(engine) as s:
        perf = s.exec(
            select(Performance).where(Performance.session_token == token)
        ).one()
        assert perf.event_id == active_event.id


def test_performer_dedupe_by_email(client, engine, songs, venue):
    _start(client, songs[0].id, email="bob@example.com")
    _start(client, songs[1].id, email="bob@example.com")
    with Session(engine) as s:
        performers = s.exec(
            select(Performer).where(Performer.email == "bob@example.com")
        ).all()
        assert len(performers) == 1


def test_start_unknown_song_404(client, venue):
    resp = _start(client, 9999)
    assert resp.status_code == 404


def test_stop_marks_finished(client, engine, songs, venue, events_log):
    token = _start(client, songs[0].id).json()["sessionId"]
    resp = client.post(f"/api/session/{token}/stop")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "finished"
    assert "recordingUrl" in body

    with Session(engine) as s:
        perf = s.exec(
            select(Performance).where(Performance.session_token == token)
        ).one()
        assert perf.status == PerformanceStatus.FINISHED
        assert perf.finished_at is not None

    assert any(name == "performance.finished" for name, _ in events_log)


def test_stop_unknown_token_404(client, venue):
    assert client.post("/api/session/nope/stop").status_code == 404
