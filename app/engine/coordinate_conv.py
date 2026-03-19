"""Coordinate conversion utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from skyfield.api import EarthSatellite, load


@dataclass
class GeodeticPoint:
    """Geodetic coordinates used by API and frontend."""

    latitude_deg: float
    longitude_deg: float
    altitude_km: float
    timestamp_utc: datetime


def propagate_tle_to_wgs84(line1: str, line2: str, when: datetime) -> GeodeticPoint:
    """Propagate TLE and convert to WGS84 coordinates using Skyfield."""
    ts = load.timescale()
    satellite = EarthSatellite(line1, line2)
    utc_when = when.astimezone(timezone.utc)
    t = ts.from_datetime(utc_when)
    subpoint = satellite.at(t).subpoint()
    return GeodeticPoint(
        latitude_deg=subpoint.latitude.degrees,
        longitude_deg=subpoint.longitude.degrees,
        altitude_km=subpoint.elevation.km,
        timestamp_utc=utc_when,
    )
