# SatProphet 部署与使用手册

## 1. 文档目标
本文档用于指导你完成 SatProphet 的本地部署、运行、验证和日常使用。

## 2. 系统组成
1. 后端服务：FastAPI，提供卫星列表、跟踪切换、预测、同步接口。
2. 数据库：PostgreSQL 16 + PostGIS，用于存储卫星、TLE 历史和空间数据。
3. 前端服务：React + Vite + Cesium，用于展示卫星状态和预测结果。

## 3. 前置条件
1. Python 3.12+。
2. Node.js 20+。
3. Podman + podman-compose（推荐），或兼容的 compose 运行方式。
4. 可访问 Space-Track（如需真实 TLE 同步）。

## 4. 环境变量配置
1. 复制模板：
```bash
cp .env.example .env
```
2. 至少确认以下变量：
- `DATABASE_URL=postgresql+psycopg://satprophet:satprophet@localhost:5432/satprophet`
- `SPACETRACK_ID=<你的账号>`
- `SPACETRACK_PASSWORD=<你的密码>`
- `CORS_ORIGINS=http://localhost:5173`
- `INGEST_INTERVAL_MINUTES=15`
- `ENABLE_SCHEDULER=true`

## 5. 安装依赖
1. Python 依赖：
```bash
uv sync --all-groups
```
2. 前端依赖：
```bash
cd web
npm install
cd ..
```

## 6. 启动数据库（Podman）
1. 启动 PostGIS：
```bash
podman compose up -d db
```
2. 检查容器状态：
```bash
podman ps --format '{{.Names}} {{.Status}}' | grep satprophet-db
```
3. 数据库迁移：
```bash
PYTHONPATH=. uv run alembic upgrade head
```
4. 健康检查（可选）：
```bash
podman exec satprophet-db pg_isready -U satprophet -d satprophet
```

## 7. 启动后端
```bash
uv run uvicorn app.main:app --reload
```
默认监听：`http://127.0.0.1:8000`

## 8. 启动前端
```bash
cd web
npm run dev
```
默认地址：`http://127.0.0.1:5173`

如需调整前端 API 地址，可在前端环境里设置 `VITE_API_BASE`。

## 9. 基础使用流程
1. 健康检查：
```bash
curl http://127.0.0.1:8000/api/v1/health
```
2. 获取 tracked 卫星列表：
```bash
curl http://127.0.0.1:8000/api/v1/satellites/tracked
```
3. 开启某颗卫星跟踪（会触发一次补丁同步）：
```bash
curl -X POST http://127.0.0.1:8000/api/v1/satellites/1/track \
  -H 'Content-Type: application/json' \
  -d '{"enable": true}'
```
4. 手动触发同步：
```bash
curl -X POST http://127.0.0.1:8000/api/v1/ingest/sync
```
5. 查询指定时刻预测：
```bash
curl "http://127.0.0.1:8000/api/v1/predict/1?t=2026-03-20T08:00:00Z"
```

## 10. 测试与验证
1. 全量测试：
```bash
uv run pytest -q
```
2. 数据库集成测试：
```bash
uv run pytest -q tests/test_db_postgis_integration.py -m db_integration
```
3. 代码质量检查：
```bash
uv run ruff check .
uv run mypy app
```
4. 前端构建验证：
```bash
cd web
npm run build
```

## 11. 常见问题排查
1. 预测接口返回 404：
- 原因：目标卫星没有可用 TLE。
- 处理：先开启跟踪并手动触发同步，再重试预测。

2. 同步失败（凭据相关）：
- 原因：Space-Track 账号或密码不正确。
- 处理：检查 `.env` 中 `SPACETRACK_ID` 和 `SPACETRACK_PASSWORD`。

3. 数据库连接失败：
- 原因：容器未启动或端口未开放。
- 处理：执行 `podman compose up -d db` 并确认 `pg_isready` 成功。

4. 前端无法请求后端：
- 原因：CORS 或 API 地址不匹配。
- 处理：检查 `CORS_ORIGINS` 与 `VITE_API_BASE`。

## 12. 停止服务
1. 停止数据库容器：
```bash
podman compose down
```
2. 停止后端和前端：
- 在各自终端使用 `Ctrl+C`。

## 13. 生产部署建议
1. 使用反向代理（如 Nginx）转发后端与前端。
2. 使用独立密钥管理替代明文 `.env`。
3. 为数据库启用持久卷备份策略。
4. 对 API 增加鉴权与限流策略。
5. 将定时同步任务日志接入集中监控。
