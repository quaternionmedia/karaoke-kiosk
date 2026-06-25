"""Performer DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class PerformerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    consent_marketing: bool | None = None


class PerformerRead(BaseModel):
    id: int
    name: str
    email: str
    consent_marketing: bool

    model_config = {"from_attributes": True}
