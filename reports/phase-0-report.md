# Phase 0 开发报告

## 阶段目标
建立项目初始化基线：工程结构、依赖定义、后端最小入口、前端最小壳层、基础文档。

## 本阶段完成内容
1. 建立目录骨架：`app/`、`web/`、`tests/`、`reports/`。
2. 完成 Python 工程定义：新增 `pyproject.toml`，采用 `uv` 工作流。
3. 完成后端最小可运行入口：
   - `app/main.py` FastAPI 应用注册。
   - `app/api/api_v1/endpoints/health.py` 健康检查接口。
   - `app/core/config.py` 环境变量配置加载。
   - `app/core/database.py` 数据库初始化占位。
4. 完成前端最小壳层：
   - `web/package.json`、`web/vite.config.ts`、`web/tsconfig.json`。
   - `web/src/App.tsx` 与 `web/src/viewer/CesiumViewer.tsx` 占位容器。
5. 补充基础工程文件：`README.md`、`.env.example`、`.gitignore`。
6. 新增测试占位：`tests/test_health_placeholder.py`。

## 安装的依赖
本阶段未执行依赖安装命令，仅完成依赖清单定义。

Python 依赖已在 `pyproject.toml` 中声明（核心）：
- fastapi
- uvicorn[standard]
- pydantic-settings
- sqlmodel
- sqlalchemy
- psycopg[binary]
- alembic
- spacetrack
- apscheduler
- astroz
- skyfield

Python 开发依赖：
- pytest
- pytest-asyncio
- ruff
- mypy

前端依赖已在 `web/package.json` 中声明：
- react
- react-dom
- cesium
- vite
- typescript
- @vitejs/plugin-react

## 当前可用功能
1. 后端已具备应用入口与健康检查路由定义：`GET /api/v1/health`。
2. 前端可作为壳层启动并展示 Cesium 区域占位。
3. 环境变量模板已就绪，支持下一阶段接入真实配置。

## 遗留与下一步（Phase 1）
1. 启动 PostgreSQL 16 + PostGIS 容器编排。
2. 设计卫星与 TLE 数据模型并创建 Alembic 初始迁移。
3. 实现最小 CRUD 以支撑 tracked 列表与跟踪状态更新。
