"""API endpoint tests for MVP core routes."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.database import get_session
from app.main import app
from app.models.satellite import Satellite
from app.models.tle import TLERecord


@pytest.fixture()
def session_factory() -> sessionmaker[Session]:
    """Create isolated in-memory session factory."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@pytest.fixture()
def client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with dependency override."""
    def override_get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def db_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Expose direct DB session for setup data."""
    with session_factory() as session:
        yield session


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tracked_satellites(client: TestClient, db_session: Session) -> None:
    db_session.add(Satellite(norad_id=25544, name="ISS", is_tracked=True))
    db_session.add(Satellite(norad_id=33591, name="NOAA-19", is_tracked=False))
    db_session.commit()

    response = client.get("/api/v1/satellites/tracked")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["norad_id"] == 25544


def test_predict_endpoint_with_missing_tle_returns_404(client: TestClient, db_session: Session) -> None:
    sat = Satellite(norad_id=25544, name="ISS", is_tracked=True)
    db_session.add(sat)
    db_session.commit()
    db_session.refresh(sat)

    now = datetime.now(timezone.utc).isoformat()
    response = client.get("/api/v1/predict/1", params={"t": now})
    assert response.status_code == 404


def test_predict_endpoint_success(client: TestClient, db_session: Session) -> None:
    sat = Satellite(norad_id=25544, name="ISS", is_tracked=True)
    db_session.add(sat)
    db_session.commit()
    db_session.refresh(sat)

    db_session.add(
        TLERecord(
            satellite_id=sat.id or 0,
            epoch=datetime(2024, 1, 1, tzinfo=timezone.utc),
            line1="1 25544U 98067A   24010.50000000  .00015000  00000+0  25000-3 0  9994",
            line2="2 25544  51.6411 100.1234 0004200  90.0000  25.0000 15.50300000000000",
            source="spacetrack",
        )
    )
    db_session.commit()

    now = datetime.now(timezone.utc).isoformat()
    response = client.get("/api/v1/predict/1", params={"t": now})
    assert response.status_code == 200
    payload = response.json()
    assert payload["satellite_id"] == 1
    assert -90.0 <= payload["latitude_deg"] <= 90.0
    assert -180.0 <= payload["longitude_deg"] <= 180.0
