"""Satellite API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class SatelliteRead(BaseModel):
    """Tracked satellite output schema."""

    id: int
    norad_id: int
    name: str
    is_tracked: bool
    updated_at: datetime


class SatelliteTrackRequest(BaseModel):
    """Track toggle request."""

    enable: bool = Field(description="Whether to enable tracking")


class SatelliteTrackResponse(BaseModel):
    """Track toggle response with patch status."""

    id: int
    norad_id: int
    is_tracked: bool
    patch: dict[str, int] | None = None
    patch_error: str | None = None
