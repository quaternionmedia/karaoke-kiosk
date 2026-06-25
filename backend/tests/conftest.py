"""Shared pytest fixtures: in-memory DB, event bus spy, and a TestClient."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import kiosk.models  # noqa: F401 - register all tables
from kiosk.app import create_app
from kiosk.config import Settings, get_settings
from kiosk.db import get_session
from kiosk.deps import get_bus
from kiosk.enums import EventStatus
from kiosk.events.bus import EventBus
from kiosk.models.event import Event
from kiosk.models.song import Song
from kiosk.models.venue import Venue
from kiosk.models.base import utcnow


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def session(engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def bus() -> EventBus:
    """A fresh bus with no default handlers, so tests attach their own spies."""
    return EventBus()


@pytest.fixture
def events_log(bus) -> list[tuple[str, object]]:
    """Records every emitted event as (name, payload)."""
    log: list[tuple[str, object]] = []
    for name in (
        "performance.started",
        "performance.finished",
        "recording.ready",
        "email.send",
    ):
        bus.subscribe(name, lambda payload, n=name: log.append((n, payload)))
    return log


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        database_url="sqlite://",
        obs_enabled=False,
        email_enabled=False,
        admin_api_key=None,
    )


@pytest.fixture
def client(engine, bus, test_settings) -> Iterator[TestClient]:
    app = create_app()

    def _get_session() -> Iterator[Session]:
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = _get_session
    app.dependency_overrides[get_bus] = lambda: bus
    app.dependency_overrides[get_settings] = lambda: test_settings

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def venue(session) -> Venue:
    venue = Venue(name="Neon Nights Karaoke", welcome_message="Welcome!")
    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


@pytest.fixture
def active_event(session, venue) -> Event:
    event = Event(
        venue_id=venue.id,
        name="Friday Night",
        starts_at=utcnow(),
        status=EventStatus.ACTIVE,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@pytest.fixture
def songs(session) -> list[Song]:
    data = [
        Song(name="Bohemian Rhapsody", artist="Queen", genre="Rock",
             duration_seconds=355, color="#f59e0b"),
        Song(name="Sweet Caroline", artist="Neil Diamond", genre="Pop",
             duration_seconds=207, color="#22c55e"),
        Song(name="Retired Track", artist="Nobody", genre="Pop",
             duration_seconds=120, is_active=False),
    ]
    session.add_all(data)
    session.commit()
    for s in data:
        session.refresh(s)
    return data
