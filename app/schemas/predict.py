"""Prediction API schemas."""

from datetime import datetime

from pydantic import BaseModel


class PredictResponse(BaseModel):
    """Prediction response payload."""

    satellite_id: int
    latitude_deg: float
    longitude_deg: float
    altitude_km: float
    timestamp_utc: datetime
