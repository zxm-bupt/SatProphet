"""
修复后 TLE 同步集成测试 - 验证 gp class 替换 tle_latest 后的功能。

运行前提：
- PostGIS 容器已启动（satprophet-db）
- 后端服务已启动（http://127.0.0.1:8000）
- 数据库中已有 TianYi B (64049) 和 TianYi C (64050) 卫星记录
"""

from __future__ import annotations

import os

import httpx
import pytest
from sqlalchemy import create_engine, text

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://satprophet:satprophet@localhost:5432/satprophet",
)


@pytest.fixture(scope="module")
def http_client() -> httpx.Client:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        yield client


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(DATABASE_URL, future=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module", autouse=True)
def seed_satellites(db_engine):
    """确保测试所需的卫星记录存在。"""
    with db_engine.begin() as conn:
        for norad_id, name in [(25544, "ISS (ZARYA)"), (64049, "TianYi B"), (64050, "TianYi C")]:
            exists = conn.execute(
                text("SELECT 1 FROM satellite WHERE norad_id = :nid"),
                {"nid": norad_id},
            ).first()
            if not exists:
                conn.execute(
                    text(
                        "INSERT INTO satellite (norad_id, name, is_tracked, created_at, updated_at) "
                        "VALUES (:nid, :name, true, NOW(), NOW())"
                    ),
                    {"nid": norad_id, "name": name},
                )
    yield


# ---------------------------------------------------------------------------
# TC-F01  TLE 同步端点正常返回
# ---------------------------------------------------------------------------

def test_tc_f01_ingest_sync_returns_200(http_client: httpx.Client) -> None:
    """TC-F01: POST /ingest/sync 应返回 200 且包含正确字段。"""
    resp = http_client.post("/ingest/sync")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "tracked" in data
    assert "fetched" in data
    assert "inserted" in data
    assert "skipped" in data
    assert data["tracked"] >= 2, f"Expected at least 2 tracked, got {data['tracked']}"
    assert data["fetched"] >= 2, f"Expected at least 2 fetched, got {data['fetched']}"


# ---------------------------------------------------------------------------
# TC-F02  TianYi B TLE 数据已入库
# ---------------------------------------------------------------------------

def test_tc_f02_tianyi_b_tle_exists(db_engine) -> None:
    """TC-F02: TianYi B (NORAD 64049) 应有 TLE 记录。"""
    with db_engine.connect() as conn:
        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM tle_record t "
                "JOIN satellite s ON t.satellite_id = s.id "
                "WHERE s.norad_id = 64049"
            )
        ).scalar_one()
    assert count >= 1, "TianYi B should have at least 1 TLE record"


# ---------------------------------------------------------------------------
# TC-F03  TianYi C TLE 数据已入库
# ---------------------------------------------------------------------------

def test_tc_f03_tianyi_c_tle_exists(db_engine) -> None:
    """TC-F03: TianYi C (NORAD 64050) 应有 TLE 记录。"""
    with db_engine.connect() as conn:
        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM tle_record t "
                "JOIN satellite s ON t.satellite_id = s.id "
                "WHERE s.norad_id = 64050"
            )
        ).scalar_one()
    assert count >= 1, "TianYi C should have at least 1 TLE record"


# ---------------------------------------------------------------------------
# TC-F04  TLE 记录包含有效的 line1/line2
# ---------------------------------------------------------------------------

def test_tc_f04_tle_lines_valid_format(db_engine) -> None:
    """TC-F04: TLE line1 应以 '1 ' 开头，line2 应以 '2 ' 开头。"""
    with db_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT t.line1, t.line2 FROM tle_record t "
                "JOIN satellite s ON t.satellite_id = s.id "
                "WHERE s.norad_id IN (64049, 64050)"
            )
        ).fetchall()
    assert len(rows) >= 2, f"Expected at least 2 TLE rows, got {len(rows)}"
    for line1, line2 in rows:
        assert line1.startswith("1 "), f"line1 should start with '1 ': {line1[:20]}"
        assert line2.startswith("2 "), f"line2 should start with '2 ': {line2[:20]}"


# ---------------------------------------------------------------------------
# TC-F05  重复同步不会重复插入（去重）
# ---------------------------------------------------------------------------

def test_tc_f05_deduplication(http_client: httpx.Client) -> None:
    """TC-F05: 再次同步应 skipped >= 2，不会重复插入相同 epoch 的 TLE。"""
    resp = http_client.post("/ingest/sync")
    assert resp.status_code == 200
    data = resp.json()
    assert data["skipped"] >= 2, f"Expected at least 2 skipped (dedup), got {data['skipped']}"


# ---------------------------------------------------------------------------
# TC-F06  追踪列表包含新增卫星
# ---------------------------------------------------------------------------

def test_tc_f06_tracked_list_contains_new_sats(http_client: httpx.Client) -> None:
    """TC-F06: GET /satellites/tracked 应包含 64049 和 64050。"""
    resp = http_client.get("/satellites/tracked")
    assert resp.status_code == 200
    data = resp.json()
    norad_ids = {s["norad_id"] for s in data}
    assert 64049 in norad_ids, "TianYi B (64049) should be in tracked list"
    assert 64050 in norad_ids, "TianYi C (64050) should be in tracked list"
