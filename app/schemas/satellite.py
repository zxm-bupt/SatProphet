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


class SatelliteCreateRequest(BaseModel):
    """Satellite create request."""

    norad_id: int = Field(description="NORAD catalog ID")
    name: str = Field(min_length=1, max_length=255, description="Satellite name")
    is_tracked: bool = Field(default=False, description="Whether tracking is enabled")


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
