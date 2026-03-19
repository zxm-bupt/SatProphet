# Phase 4 开发报告

## 阶段目标
完成 API 业务闭环：tracked 列表、track 配置、预测查询与统一 schema。

## 本阶段完成内容
1. 新增 schema：
   - `app/schemas/satellite.py`
   - `app/schemas/predict.py`
   - `app/schemas/ingest.py`
2. 新增端点：
   - `GET /api/v1/satellites/tracked`
   - `POST /api/v1/satellites/{id}/track`
   - `GET /api/v1/predict/{id}?t=...`
   - `POST /api/v1/ingest/sync`
3. 路由注册与应用入口增强：
   - `app/api/api_v1/api.py`
   - `app/main.py`（lifespan + CORS + scheduler 生命周期控制）
4. 增强配置项：
   - `CORS_ORIGINS`
   - `INGEST_INTERVAL_MINUTES`
   - `ENABLE_SCHEDULER`

## 安装的依赖
本阶段未执行依赖安装命令。

## 当前可用功能
1. 可获取 tracked 卫星列表。
2. 可切换卫星跟踪状态并触发一次 TLE 补丁同步。
3. 可按时间参数请求预测坐标。
4. 可手动触发全量 tracked 同步。