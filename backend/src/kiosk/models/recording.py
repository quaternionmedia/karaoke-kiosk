"""Recording model — recording state for a performance (one-to-one)."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from kiosk.enums import RecordingStatus
from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.performance import Performance


class Recording(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    performance_id: int = Field(foreign_key="performance.id", unique=True, index=True)
    status: RecordingStatus = Field(default=RecordingStatus.PENDING, index=True)
    # The shareable URL returned to the frontend as ``recordingUrl`` (may be null).
    url: str | None = None
    # Local file path from the OBS recording output.
    file_path: str | None = None
    shared_at: datetime | None = None
    error: str | None = None

    performance: "Performance" = Relationship(back_populates="recording")
