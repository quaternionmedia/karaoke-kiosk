"""Admin settings endpoint (read-only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from kiosk.config import Settings, get_settings
from kiosk.deps import admin_guard
from kiosk.schemas.settings import SettingsRead

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin:settings"],
    dependencies=[Depends(admin_guard)],
)

# Fields that should be masked (show "••••" when set, null when unset)
SECRET_FIELDS = frozenset({
    "database_url",
    "smtp_password",
    "obs_ws_password",
    "admin_api_key",
})


def _mask_value(key: str, value: str | None) -> str | None:
    """Mask a secret value if it's set."""
    if key in SECRET_FIELDS:
        return "••••" if value else None
    return value


@admin_router.get("/settings", response_model=SettingsRead)
def get_settings_read(settings: Settings = Depends(get_settings)) -> SettingsRead:
    """Get read-only environment settings with secrets masked.
    
    Database URL and SMTP/OBS passwords are replaced with "••••" when set.
    """
    return SettingsRead(
        database_url=_mask_value("database_url", settings.database_url),
        cors_origins=settings.cors_origins,
        obs_enabled=settings.obs_enabled,
        obs_ws_url=settings.obs_ws_url,
        obs_ws_password=_mask_value("obs_ws_password", settings.obs_ws_password),
        email_enabled=settings.email_enabled,
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=_mask_value("smtp_password", settings.smtp_password),
        smtp_from=settings.smtp_from,
        recording_base_url=settings.recording_base_url,
        admin_api_key=_mask_value("admin_api_key", settings.admin_api_key),
    )
