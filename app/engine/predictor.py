"""Prediction service bridging database TLE and coordinate conversion."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session

from app.crud.tle import get_latest_tle_by_satellite_id
from app.engine.astroz_wrapper import AstrozPropagator
from app.engine.coordinate_conv import GeodeticPoint, propagate_tle_to_wgs84


def predict_geodetic(session: Session, satellite_id: int, when: datetime) -> GeodeticPoint | None:
    """Predict geodetic coordinates for one satellite at a given timestamp."""
    tle = get_latest_tle_by_satellite_id(session, satellite_id)
    if tle is None:
        return None

    propagator = AstrozPropagator()
    # For MVP stability we use Skyfield conversion path directly.
    # Astroz integration hook is kept for Phase 3 enhancement without API changes.
    _ = propagator.available
    return propagate_tle_to_wgs84(tle.line1, tle.line2, when)
