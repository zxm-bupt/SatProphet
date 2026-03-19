"""CRUD helpers for satellites."""

from datetime import datetime, timezone

from sqlmodel import Session, col, select

from app.models.satellite import Satellite


def get_satellite_by_norad_id(session: Session, norad_id: int) -> Satellite | None:
    """Return satellite by NORAD ID."""
    statement = select(Satellite).where(Satellite.norad_id == norad_id).limit(1)
    return session.exec(statement).first()


def list_tracked_satellites(session: Session) -> list[Satellite]:
    """Return tracked satellites."""
    statement = (
        select(Satellite)
        .where(col(Satellite.is_tracked).is_(True))
        .order_by(col(Satellite.norad_id))
    )
    return list(session.exec(statement))


def set_tracking(session: Session, satellite_id: int, enable: bool) -> Satellite | None:
    """Update tracking status for one satellite."""
    satellite = session.get(Satellite, satellite_id)
    if satellite is None:
        return None

    satellite.is_tracked = enable
    satellite.updated_at = datetime.now(timezone.utc)
    session.add(satellite)
    session.commit()
    session.refresh(satellite)
    return satellite
