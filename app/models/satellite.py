"""Satellite data models."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import utcnow


class Satellite(SQLModel, table=True):
    """Tracked satellite metadata."""

    id: Optional[int] = Field(default=None, primary_key=True)
    norad_id: int = Field(index=True, unique=True)
    name: str = Field(max_length=255)
    is_tracked: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
