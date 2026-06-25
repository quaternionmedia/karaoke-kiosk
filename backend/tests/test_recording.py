"""Recording share endpoint tests."""

from __future__ import annotations

from sqlmodel import Session, select

from kiosk.models.recording import Recording
from kiosk.models.performance import Performance


def _start(client, song_id):
    return client.post(
        "/api/session/start",
        json={"songId": song_id, "singer": {"name": "Al", "email": "al@x.com"}},
    ).json()["sessionId"]


def test_share_returns_204_and_emits(client, engine, songs, venue, events_log):
    token = _start(client, songs[0].id)
    client.post(f"/api/session/{token}/stop")

    resp = client.post(
        "/api/recording/share", json={"email": "al@x.com", "sessionId": token}
    )
    assert resp.status_code == 204

    emitted = {name for name, _ in events_log}
    assert "recording.ready" in emitted
    assert "email.send" in emitted

    with Session(engine) as s:
        perf = s.exec(
            select(Performance).where(Performance.session_token == token)
        ).one()
        rec = s.exec(
            select(Recording).where(Recording.performance_id == perf.id)
        ).one()
        assert rec.shared_at is not None


def test_share_unknown_session_404(client, venue):
    resp = client.post(
        "/api/recording/share", json={"email": "a@b.com", "sessionId": "nope"}
    )
    assert resp.status_code == 404


def test_share_email_uses_venue_template(client, engine, songs, active_event, events_log):
    # active_event ensures the performance links to a venue for templating.
    client_session_token = _start(client, songs[0].id)
    client.post(f"/api/session/{client_session_token}/stop")
    client.post(
        "/api/recording/share",
        json={"email": "al@x.com", "sessionId": client_session_token},
    )
    email_payloads = [p for n, p in events_log if n == "email.send"]
    assert email_payloads
    payload = email_payloads[-1]
    assert payload.to == "al@x.com"
    assert "Bohemian Rhapsody" in payload.body
