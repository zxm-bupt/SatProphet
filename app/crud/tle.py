"""CRUD helpers for TLE history."""

from sqlmodel import Session, col, select

from app.models.tle import TLERecord


def get_latest_tle_by_satellite_id(session: Session, satellite_id: int) -> TLERecord | None:
    """Return latest TLE record for a satellite."""
    statement = (
        select(TLERecord)
        .where(TLERecord.satellite_id == satellite_id)
        .order_by(col(TLERecord.epoch).desc())
        .limit(1)
    )
    return session.exec(statement).first()
