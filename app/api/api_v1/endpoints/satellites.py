"""Satellite endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.crud.satellites import list_tracked_satellites, set_tracking
from app.ingester.service import sync_tle_for_satellite
from app.schemas.satellite import SatelliteRead, SatelliteTrackRequest, SatelliteTrackResponse

router = APIRouter(prefix="/satellites", tags=["satellites"])


@router.get("/tracked", response_model=list[SatelliteRead])
async def get_tracked_satellites(session: Session = Depends(get_session)) -> list[SatelliteRead]:
    """Return currently tracked satellites."""
    satellites = list_tracked_satellites(session)
    return [
        SatelliteRead(
            id=item.id or 0,
            norad_id=item.norad_id,
            name=item.name,
            is_tracked=item.is_tracked,
            updated_at=item.updated_at,
        )
        for item in satellites
    ]


@router.post("/{satellite_id}/track", response_model=SatelliteTrackResponse)
async def configure_tracking(
    satellite_id: int,
    payload: SatelliteTrackRequest,
    session: Session = Depends(get_session),
) -> SatelliteTrackResponse:
    """Set tracking status and trigger one TLE patch sync."""
    satellite = set_tracking(session, satellite_id=satellite_id, enable=payload.enable)
    if satellite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Satellite not found")

    patch_result: dict[str, int] | None = None
    patch_error: str | None = None

    if satellite.is_tracked:
        try:
            patch_result = sync_tle_for_satellite(session, satellite)
        except Exception as exc:  # pragma: no cover - external network path
            patch_error = str(exc)

    return SatelliteTrackResponse(
        id=satellite.id or 0,
        norad_id=satellite.norad_id,
        is_tracked=satellite.is_tracked,
        patch=patch_result,
        patch_error=patch_error,
    )
