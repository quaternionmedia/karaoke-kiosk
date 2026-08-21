"""Email template DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class EmailTemplateCreate(BaseModel):
    venue_id: int
    slug: str
    name: str
    subject: str
    body: str
    is_active: bool = True


class EmailTemplateUpdate(BaseModel):
    slug: str | None = None
    name: str | None = None
    subject: str | None = None
    body: str | None = None
    is_active: bool | None = None


class EmailTemplateRead(BaseModel):
    id: int
    venue_id: int
    slug: str
    name: str
    subject: str
    body: str
    is_active: bool

    model_config = {"from_attributes": True}
