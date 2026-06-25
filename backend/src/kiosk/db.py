"""Database engine and session management."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from kiosk.config import get_settings

# Import the models package so every table is registered on ``SQLModel.metadata``
# before ``create_all`` / Alembic autogenerate run.
import kiosk.models  # noqa: F401

_engine: Engine | None = None


def _connect_args(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        # FastAPI/TestClient may touch the connection from worker threads.
        return {"check_same_thread": False}
    return {}


def get_engine() -> Engine:
    """Return the process-wide engine, building it on first use."""
    global _engine
    if _engine is None:
        url = get_settings().database_url
        _engine = create_engine(url, connect_args=_connect_args(url))
    return _engine


def init_db() -> None:
    """Create all tables. Used for dev/tests; production uses Alembic."""
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a database session."""
    with Session(get_engine()) as session:
        yield session
