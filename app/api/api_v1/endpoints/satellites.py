"""Satellite endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.crud.satellites import (
    create_satellite,
    get_satellite_by_norad_id,
    list_satellites,
    list_tracked_satellites,
    set_tracking,
)
from app.ingester.service import sync_tle_for_satellite
from app.schemas.satellite import (
    SatelliteCreateRequest,
    SatelliteRead,
    SatelliteTrackRequest,
    SatelliteTrackResponse,
)

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


@router.get("", response_model=list[SatelliteRead])
async def get_all_satellites(session: Session = Depends(get_session)) -> list[SatelliteRead]:
    """Return all satellites in database."""
    satellites = list_satellites(session)
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


@router.post("", response_model=SatelliteRead, status_code=status.HTTP_201_CREATED)
async def create_satellite_endpoint(
    payload: SatelliteCreateRequest,
    session: Session = Depends(get_session),
) -> SatelliteRead:
    """Create a new satellite."""
    existing = get_satellite_by_norad_id(session, payload.norad_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Satellite with NORAD {payload.norad_id} already exists",
        )

    created = create_satellite(
        session=session,
        norad_id=payload.norad_id,
        name=payload.name,
        is_tracked=payload.is_tracked,
    )
    return SatelliteRead(
        id=created.id or 0,
        norad_id=created.norad_id,
        name=created.name,
        is_tracked=created.is_tracked,
        updated_at=created.updated_at,
    )


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
