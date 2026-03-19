"""TLE data models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class TLERecord(SQLModel, table=True):
    """TLE history record."""

    __tablename__ = "tle_record"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    satellite_id: int = Field(foreign_key="satellite.id", index=True)
    epoch: datetime = Field(index=True, nullable=False)
    line1: str = Field(max_length=128)
    line2: str = Field(max_length=128)
    source: str = Field(default="spacetrack", max_length=64)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
