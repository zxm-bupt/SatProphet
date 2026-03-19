"""Satellite ground track snapshot model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class SatelliteGroundTrack(SQLModel, table=True):
    """Stores latest geodetic snapshot for quick lookup.

    Notes:
        Geometry/Geography point is intentionally deferred to Phase 1 migration
        once PostGIS extension is guaranteed in all environments.
    """

    __tablename__ = "satellite_ground_track"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    satellite_id: int = Field(foreign_key="satellite.id", index=True, unique=True)
    latitude_deg: float = Field(sa_column=Column(DOUBLE_PRECISION, nullable=False))
    longitude_deg: float = Field(sa_column=Column(DOUBLE_PRECISION, nullable=False))
    altitude_km: float = Field(sa_column=Column(DOUBLE_PRECISION, nullable=False))
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
