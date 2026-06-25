"""Session lifecycle DTOs — the frontend-facing contract.

Field names use camelCase aliases to match frontend/src/api/index.ts.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Singer(BaseModel):
    name: str
    email: str = ""


class SessionStartRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    song_id: int = Field(alias="songId")
    singer: Singer


class SessionStartResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(serialization_alias="sessionId")
    status: str = "playing"


class StopResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    recording_url: str | None = Field(default=None, serialization_alias="recordingUrl")
    status: str = "finished"


class ShareRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str
    session_id: str = Field(alias="sessionId")
