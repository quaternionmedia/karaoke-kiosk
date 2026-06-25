"""Performer model — a singer identified by name and email."""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from kiosk.models.base import TimestampMixin

if TYPE_CHECKING:
    from kiosk.models.performance import Performance


class Performer(TimestampMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    email: str = Field(index=True)
    consent_marketing: bool = False

    performances: list["Performance"] = Relationship(back_populates="performer")
