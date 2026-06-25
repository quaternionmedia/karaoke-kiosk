"""Application settings, loaded from the environment (and an optional ``.env``)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the kiosk backend.

    Every value can be overridden via an environment variable of the same name
    (case-insensitive), e.g. ``DATABASE_URL`` or ``OBS_ENABLED``.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database -------------------------------------------------------------
    database_url: str = "sqlite:///./kiosk.db"

    # CORS -----------------------------------------------------------------
    # The Vite dev server runs on its own origin with no proxy, so the browser
    # needs these origins allow-listed to call the API.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # OBS scene/recording integration (handlers are stubs until enabled) ----
    obs_enabled: bool = False
    obs_ws_url: str = "ws://127.0.0.1:4455"
    obs_ws_password: str | None = None

    # Email / recording sharing (handlers are stubs until enabled) ---------
    email_enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    # Turns OBS output file paths into shareable URLs.
    recording_base_url: str | None = None

    # Admin auth: when set, the shared-secret header guard is enforced.
    admin_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton (overridable in tests)."""
    return Settings()
