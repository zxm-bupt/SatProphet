"""TLE ingestion service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, col, select

from app.crud.satellites import get_satellite_by_norad_id
from app.models.satellite import Satellite
from app.models.tle import TLERecord
from app.ingester.spacetrack_client import SpaceTrackGateway


def _parse_epoch(value: str) -> datetime:
    """Parse Space-Track epoch string into datetime."""
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _upsert_tle_record(
    session: Session,
    satellite_id: int,
    epoch: datetime,
    line1: str,
    line2: str,
) -> bool:
    """Insert a TLE record if the (satellite, epoch) tuple is new.

    Returns:
        True if inserted, False if it already existed.
    """
    existing = session.exec(
        select(TLERecord)
        .where(TLERecord.satellite_id == satellite_id)
        .where(TLERecord.epoch == epoch)
    ).first()
    if existing is not None:
        return False

    session.add(
        TLERecord(
            satellite_id=satellite_id,
            epoch=epoch,
            line1=line1,
            line2=line2,
            source="spacetrack",
        )
    )
    return True


def _ensure_satellite_from_payload(session: Session, payload: dict[str, Any]) -> Satellite:
    """Create missing satellite rows based on Space-Track payload."""
    norad_id = int(payload["NORAD_CAT_ID"])
    satellite = get_satellite_by_norad_id(session, norad_id)
    if satellite is not None:
        return satellite

    name = str(payload.get("OBJECT_NAME") or f"NORAD-{norad_id}")
    satellite = Satellite(norad_id=norad_id, name=name, is_tracked=True)
    session.add(satellite)
    session.flush()
    return satellite


def sync_tracked_tles(session: Session, gateway: SpaceTrackGateway | None = None) -> dict[str, int]:
    """Synchronize latest TLE for all tracked satellites."""
    gateway = gateway or SpaceTrackGateway()
    tracked = session.exec(select(Satellite).where(col(Satellite.is_tracked).is_(True))).all()
    norad_ids = [item.norad_id for item in tracked]

    payloads = gateway.fetch_latest_tle(norad_ids)
    inserted = 0
    skipped = 0

    for row in payloads:
        satellite = _ensure_satellite_from_payload(session, row)
        epoch = _parse_epoch(str(row["EPOCH"]))
        line1 = str(row["TLE_LINE1"])
        line2 = str(row["TLE_LINE2"])
        if _upsert_tle_record(session, satellite.id or 0, epoch, line1, line2):
            inserted += 1
        else:
            skipped += 1

    session.commit()
    return {"tracked": len(norad_ids), "fetched": len(payloads), "inserted": inserted, "skipped": skipped}


def sync_tle_for_satellite(
    session: Session,
    satellite: Satellite,
    gateway: SpaceTrackGateway | None = None,
) -> dict[str, int]:
    """Synchronize latest TLE for one satellite."""
    gateway = gateway or SpaceTrackGateway()
    payloads = gateway.fetch_latest_tle([satellite.norad_id])
    inserted = 0
    skipped = 0

    for row in payloads:
        epoch = _parse_epoch(str(row["EPOCH"]))
        line1 = str(row["TLE_LINE1"])
        line2 = str(row["TLE_LINE2"])
        if _upsert_tle_record(session, satellite.id or 0, epoch, line1, line2):
            inserted += 1
        else:
            skipped += 1

    session.commit()
    return {"fetched": len(payloads), "inserted": inserted, "skipped": skipped}
