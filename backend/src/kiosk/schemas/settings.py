"""Settings DTOs (read-only, admin-only)."""

from __future__ import annotations

from pydantic import BaseModel


class SettingsRead(BaseModel):
    """Read-only environment settings with secrets masked."""
    
    database_url: str | None
    cors_origins: list[str]
    obs_enabled: bool
    obs_ws_url: str | None
    obs_ws_password: str | None  # masked
    email_enabled: bool
    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_password: str | None  # masked
    smtp_from: str | None
    recording_base_url: str | None
    admin_api_key: str | None  # masked
