"""Prediction endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.engine.predictor import predict_geodetic
from app.schemas.predict import PredictResponse

router = APIRouter(prefix="/predict", tags=["predict"])


@router.get("/{satellite_id}", response_model=PredictResponse)
async def predict_satellite_position(
    satellite_id: int,
    t: datetime = Query(description="Prediction timestamp in ISO8601"),
    session: Session = Depends(get_session),
) -> PredictResponse:
    """Predict one satellite geodetic position at given timestamp."""
    when = t.astimezone(timezone.utc)
    point = predict_geodetic(session=session, satellite_id=satellite_id, when=when)
    if point is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TLE not found for satellite")

    return PredictResponse(
        satellite_id=satellite_id,
        latitude_deg=point.latitude_deg,
        longitude_deg=point.longitude_deg,
        altitude_km=point.altitude_km,
        timestamp_utc=point.timestamp_utc,
    )
