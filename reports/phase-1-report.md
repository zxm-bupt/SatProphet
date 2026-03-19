# Phase 1 开发报告

## 阶段目标
完成持久化层基础能力：数据库编排、数据模型、迁移基线与最小 CRUD。

## 本阶段完成内容
1. 新增数据库编排：
   - `docker-compose.yml` 使用 PostgreSQL 16 + PostGIS。
   - `docker/postgres/init.sql` 启用 `postgis` 扩展。
2. 新增模型定义：
   - `app/models/satellite.py`（卫星元数据与跟踪状态）。
   - `app/models/tle.py`（TLE 历史记录）。
   - `app/models/satellite_ground_track.py`（地影点快照与经纬高字段）。
3. 新增数据库会话与依赖：
   - `app/core/database.py` 增加 `get_session()`。
4. 新增最小 CRUD：
   - `app/crud/satellites.py`（tracked 列表、跟踪状态更新）。
   - `app/crud/tle.py`（读取最新 TLE）。
5. 建立 Alembic 基线：
   - `alembic.ini`。
   - `migrations/env.py`。
   - `migrations/versions/20260317_0001_init_schema.py` 初始迁移脚本。
6. 更新文档：`README.md` 增加数据库启动与迁移执行命令。

## 安装的依赖
本阶段未执行依赖安装命令，仅延续 Phase 0 的依赖声明。

## 当前可用功能
1. 本地可通过 `docker compose up -d db` 启动 PostGIS 数据库。
2. 可通过 `uv run alembic upgrade head` 应用初始数据库结构。
3. 应用已具备基础数据访问入口（Session + CRUD）。

## 遗留与下一步（Phase 2）
1. 实现 Space-Track 客户端与认证。
2. 实现增量同步逻辑（按 tracked + epoch 去重）。
3. 接入 APScheduler 的手动与定时触发入口。
