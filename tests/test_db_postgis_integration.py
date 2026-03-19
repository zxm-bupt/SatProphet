"""PostGIS integration tests for containerized database."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text


@pytest.fixture(scope="module")
def db_engine():
    """Create engine for real PostGIS integration testing."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://satprophet:satprophet@localhost:5432/satprophet",
    )
    engine = create_engine(database_url, future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - environment-dependent
        pytest.skip(f"PostGIS is not reachable: {exc}")

    yield engine
    engine.dispose()


@pytest.mark.db_integration
def test_postgis_extension_enabled(db_engine) -> None:
    """Verify PostGIS extension is available."""
    with db_engine.connect() as conn:
        version = conn.execute(text("SELECT postgis_version()"))
        value = version.scalar_one()
    assert isinstance(value, str)
    assert len(value) > 0


@pytest.mark.db_integration
def test_core_tables_exist_after_migration(db_engine) -> None:
    """Verify Alembic-created core tables are present."""
    expected = {"satellite", "tle_record", "satellite_ground_track", "alembic_version"}
    with db_engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
        )
        names = {row[0] for row in rows}
    assert expected.issubset(names)


@pytest.mark.db_integration
def test_geography_column_and_spatial_query(db_engine) -> None:
    """Verify geography column exists and supports ST_DWithin."""
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM satellite_ground_track"))
        conn.execute(text("DELETE FROM tle_record"))
        conn.execute(text("DELETE FROM satellite"))

        sat_id = conn.execute(
            text(
                """
                INSERT INTO satellite (norad_id, name, is_tracked, created_at, updated_at)
                VALUES (:norad_id, :name, true, now(), now())
                RETURNING id
                """
            ),
            {"norad_id": 999001, "name": "DB-TEST-SAT"},
        ).scalar_one()

        conn.execute(
            text(
                """
                INSERT INTO satellite_ground_track (
                    satellite_id,
                    latitude_deg,
                    longitude_deg,
                    altitude_km,
                    updated_at,
                    ground_point
                )
                VALUES (
                    :satellite_id,
                    :lat,
                    :lon,
                    :alt,
                    now(),
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                )
                """
            ),
            {
                "satellite_id": sat_id,
                "lat": 30.0,
                "lon": 120.0,
                "alt": 550.0,
            },
        )

        count = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM satellite_ground_track
                WHERE ST_DWithin(
                    ground_point,
                    ST_SetSRID(ST_MakePoint(120.001, 30.001), 4326)::geography,
                    500
                )
                """
            )
        ).scalar_one()

    assert count == 1
