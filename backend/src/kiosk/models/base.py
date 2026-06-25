"""Shared model mixins."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp factory."""
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    """Adds ``created_at`` / ``updated_at`` columns to a table model."""

    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": utcnow},
    )
