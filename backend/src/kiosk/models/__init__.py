"""Model package — imports every table so ``SQLModel.metadata`` is complete.

Anything that needs the full schema (``create_all``, Alembic autogenerate)
should ``import kiosk.models`` to guarantee all tables are registered.
"""

from kiosk.models.event import Event
from kiosk.models.performance import Performance
from kiosk.models.performer import Performer
from kiosk.models.recording import Recording
from kiosk.models.song import Song, SongTagLink, Tag
from kiosk.models.venue import Venue

__all__ = [
    "Event",
    "Performance",
    "Performer",
    "Recording",
    "Song",
    "SongTagLink",
    "Tag",
    "Venue",
]
