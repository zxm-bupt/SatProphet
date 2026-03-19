"""Tests for ingester synchronization logic."""

from __future__ import annotations

from sqlmodel import Session, SQLModel, create_engine, select

from app.ingester.service import sync_tracked_tles
from app.models.satellite import Satellite
from app.models.tle import TLERecord


class FakeGateway:
    """Simple fake gateway for deterministic service tests."""

    def __init__(self, payloads: list[dict[str, str]]) -> None:
        self.payloads = payloads

    def fetch_latest_tle(self, norad_ids: list[int]) -> list[dict[str, str]]:
        _ = norad_ids
        return self.payloads


def test_sync_tracked_tles_inserts_and_deduplicates() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Satellite(norad_id=25544, name="ISS", is_tracked=True))
        session.commit()

    payload = {
        "NORAD_CAT_ID": "25544",
        "OBJECT_NAME": "ISS",
        "EPOCH": "2026-03-17T00:00:00+00:00",
        "TLE_LINE1": "1 25544U 98067A   26077.00000000  .00015000  00000+0  25000-3 0  9994",
        "TLE_LINE2": "2 25544  51.6411 100.1234 0004200  90.0000  25.0000 15.50300000000000",
    }

    with Session(engine) as session:
        first = sync_tracked_tles(session, gateway=FakeGateway([payload]))
        second = sync_tracked_tles(session, gateway=FakeGateway([payload]))

        count = len(session.exec(select(TLERecord)).all())

    assert first["inserted"] == 1
    assert second["skipped"] == 1
    assert count == 1


def test_sync_tracked_tles_ignores_empty_list() -> None:
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        result = sync_tracked_tles(session, gateway=FakeGateway([]))

    assert result == {"tracked": 0, "fetched": 0, "inserted": 0, "skipped": 0}
