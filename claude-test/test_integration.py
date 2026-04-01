"""
SatProphet 集成测试 - 针对实际运行的后端服务和 PostGIS 数据库。

运行前提：
- PostGIS 容器已启动（satprophet-db）
- 后端服务已启动（http://127.0.0.1:8000）
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx
import pytest
from sqlalchemy import create_engine, text

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://satprophet:satprophet@localhost:5432/satprophet",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def http_client() -> httpx.Client:
    """Shared HTTP client for the live backend."""
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        yield client


@pytest.fixture(scope="session")
def db_engine():
    """Shared SQLAlchemy engine against the real PostGIS container."""
    engine = create_engine(DATABASE_URL, future=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"PostGIS is not reachable: {exc}")
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def clean_db(db_engine):
    """Truncate test tables before the test session, restore after."""
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM satellite_ground_track"))
        conn.execute(text("DELETE FROM tle_record"))
        conn.execute(text("DELETE FROM satellite"))
    yield db_engine
    # cleanup after session
    with db_engine.begin() as conn:
        conn.execute(text("DELETE FROM satellite_ground_track"))
        conn.execute(text("DELETE FROM tle_record"))
        conn.execute(text("DELETE FROM satellite"))


# ---------------------------------------------------------------------------
# TC-01  Health endpoint
# ---------------------------------------------------------------------------


def test_tc01_health(http_client: httpx.Client) -> None:
    """TC-01: GET /health 应返回 200 和 {'status': 'ok'}。"""
    resp = http_client.get("/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert resp.json() == {"status": "ok"}, f"Unexpected body: {resp.json()}"


# ---------------------------------------------------------------------------
# TC-02  数据库连通性
# ---------------------------------------------------------------------------


def test_tc02_db_connectivity(clean_db) -> None:
    """TC-02: 数据库可以正常连接并执行查询。"""
    with clean_db.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
    assert result == 1


# ---------------------------------------------------------------------------
# TC-03  PostGIS 扩展
# ---------------------------------------------------------------------------


def test_tc03_postgis_extension(clean_db) -> None:
    """TC-03: PostGIS 扩展已启用。"""
    with clean_db.connect() as conn:
        version = conn.execute(text("SELECT postgis_version()")).scalar_one()
    assert isinstance(version, str) and len(version) > 0, "postgis_version() should return a string"


# ---------------------------------------------------------------------------
# TC-04  迁移表存在
# ---------------------------------------------------------------------------


def test_tc04_tables_exist(clean_db) -> None:
    """TC-04: Alembic 迁移已创建核心业务表。"""
    expected = {"satellite", "tle_record", "satellite_ground_track", "alembic_version"}
    with clean_db.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )
        )
        actual = {r[0] for r in rows}
    assert expected.issubset(actual), f"Missing tables: {expected - actual}"


# ---------------------------------------------------------------------------
# TC-05  空卫星列表
# ---------------------------------------------------------------------------


def test_tc05_empty_tracked_satellites(http_client: httpx.Client, clean_db) -> None:
    """TC-05: 数据库空时 /satellites/tracked 应返回空列表。"""
    resp = http_client.get("/satellites/tracked")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# TC-06  插入卫星后列表不为空
# ---------------------------------------------------------------------------


def test_tc06_tracked_satellites_after_insert(http_client: httpx.Client, clean_db) -> None:
    """TC-06: 插入 tracked 卫星后 /satellites/tracked 应返回该卫星。"""
    with clean_db.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO satellite (norad_id, name, is_tracked, created_at, updated_at) "
                "VALUES (25544, 'ISS', true, now(), now())"
            )
        )

    resp = http_client.get("/satellites/tracked")
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload) >= 1
    norad_ids = [s["norad_id"] for s in payload]
    assert 25544 in norad_ids


# ---------------------------------------------------------------------------
# TC-07  非跟踪卫星不出现在列表中
# ---------------------------------------------------------------------------


def test_tc07_untracked_satellite_not_in_list(http_client: httpx.Client, clean_db) -> None:
    """TC-07: is_tracked=false 的卫星不出现在 /satellites/tracked 中。"""
    with clean_db.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO satellite (norad_id, name, is_tracked, created_at, updated_at) "
                "VALUES (33591, 'NOAA-19', false, now(), now())"
            )
        )

    resp = http_client.get("/satellites/tracked")
    assert resp.status_code == 200
    norad_ids = [s["norad_id"] for s in resp.json()]
    assert 33591 not in norad_ids


# ---------------------------------------------------------------------------
# TC-08  无 TLE 预测返回 404
# ---------------------------------------------------------------------------


def test_tc08_predict_no_tle_returns_404(http_client: httpx.Client, clean_db) -> None:
    """TC-08: 无 TLE 记录时 /predict/{id} 应返回 404。"""
    with clean_db.connect() as conn:
        sat_id = conn.execute(
            text("SELECT id FROM satellite WHERE norad_id=25544")
        ).scalar_one_or_none()

    if sat_id is None:
        pytest.skip("Satellite 25544 not found in DB (depends on TC-06)")

    now = datetime.now(timezone.utc).isoformat()
    resp = http_client.get(f"/predict/{sat_id}", params={"t": now})
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# TC-09  插入 TLE 后预测成功
# ---------------------------------------------------------------------------


def test_tc09_predict_with_tle_returns_position(http_client: httpx.Client, clean_db) -> None:
    """TC-09: 有 TLE 记录时 /predict/{id} 应返回合法的经纬度。"""
    with clean_db.begin() as conn:
        sat_id = conn.execute(
            text("SELECT id FROM satellite WHERE norad_id=25544")
        ).scalar_one_or_none()

        if sat_id is None:
            conn.execute(
                text(
                    "INSERT INTO satellite (norad_id, name, is_tracked, created_at, updated_at) "
                    "VALUES (25544, 'ISS', true, now(), now())"
                )
            )
            sat_id = conn.execute(
                text("SELECT id FROM satellite WHERE norad_id=25544")
            ).scalar_one()

        # 清除旧 TLE，插入新的
        conn.execute(text("DELETE FROM tle_record WHERE satellite_id=:sid"), {"sid": sat_id})
        conn.execute(
            text(
                "INSERT INTO tle_record "
                "(satellite_id, epoch, line1, line2, source, created_at) "
                "VALUES (:sid, :epoch, :l1, :l2, 'spacetrack', now())"
            ),
            {
                "sid": sat_id,
                "epoch": datetime(2024, 1, 1, tzinfo=timezone.utc),
                "l1": "1 25544U 98067A   24010.50000000  .00015000  00000+0  25000-3 0  9994",
                "l2": "2 25544  51.6411 100.1234 0004200  90.0000  25.0000 15.50300000000000",
            },
        )

    now = datetime.now(timezone.utc).isoformat()
    resp = http_client.get(f"/predict/{sat_id}", params={"t": now})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    payload = resp.json()
    assert payload["satellite_id"] == sat_id
    assert -90.0 <= payload["latitude_deg"] <= 90.0
    assert -180.0 <= payload["longitude_deg"] <= 180.0
    assert payload["altitude_km"] > 0


# ---------------------------------------------------------------------------
# TC-10  PostGIS 地理空间查询
# ---------------------------------------------------------------------------


def test_tc10_spatial_query(clean_db) -> None:
    """TC-10: ST_DWithin 地理空间查询可以正常工作。"""
    with clean_db.begin() as conn:
        sat_id = conn.execute(
            text("SELECT id FROM satellite WHERE norad_id=25544")
        ).scalar_one_or_none()

        if sat_id is None:
            conn.execute(
                text(
                    "INSERT INTO satellite (norad_id, name, is_tracked, created_at, updated_at) "
                    "VALUES (25544, 'ISS', true, now(), now())"
                )
            )
            sat_id = conn.execute(
                text("SELECT id FROM satellite WHERE norad_id=25544")
            ).scalar_one()

        # 插入地面轨迹点
        conn.execute(text("DELETE FROM satellite_ground_track WHERE satellite_id=:sid"), {"sid": sat_id})
        conn.execute(
            text(
                "INSERT INTO satellite_ground_track "
                "(satellite_id, latitude_deg, longitude_deg, altitude_km, updated_at, ground_point) "
                "VALUES (:sid, 30.0, 120.0, 550.0, now(), "
                "ST_SetSRID(ST_MakePoint(120.0, 30.0), 4326)::geography)"
            ),
            {"sid": sat_id},
        )

        # 查询 500m 范围内的点（120.001, 30.001 ≈ 139m 误差）
        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM satellite_ground_track "
                "WHERE ST_DWithin(ground_point, "
                "ST_SetSRID(ST_MakePoint(120.001, 30.001), 4326)::geography, 500)"
            )
        ).scalar_one()

    assert count >= 1, "ST_DWithin should find the nearby ground track point"


# ---------------------------------------------------------------------------
# TC-11  API 文档端点可访问
# ---------------------------------------------------------------------------


def test_tc11_openapi_docs_accessible(http_client: httpx.Client) -> None:
    """TC-11: FastAPI 自动生成的 OpenAPI 文档应可访问。"""
    # httpx client base_url is /api/v1, docs are at /docs
    resp = httpx.get("http://127.0.0.1:8000/docs", timeout=5)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# TC-12  Alembic 版本确认
# ---------------------------------------------------------------------------


def test_tc12_alembic_version(clean_db) -> None:
    """TC-12: alembic_version 表有且只有一行（head 版本）。"""
    with clean_db.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM alembic_version")).scalar_one()
    assert count == 1, f"Expected 1 alembic_version row, got {count}"
