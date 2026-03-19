# Phase 2 开发报告

## 阶段目标
实现 Ingester 与数据同步：Space-Track 接入、按 tracked 增量同步、调度与手动触发入口。

## 本阶段完成内容
1. 新增 Space-Track 网关：`app/ingester/spacetrack_client.py`
   - 读取 `.env` 中 `SPACETRACK_ID` / `SPACETRACK_PASSWORD`。
   - 本地内存限流窗口（30/分钟，300/小时）。
   - 拉取 `tle_latest` 最新记录。
2. 新增同步服务：`app/ingester/service.py`
   - tracked 卫星列表同步。
   - 单卫星补丁同步（供 track 接口触发）。
   - 按 `(satellite_id, epoch)` 去重入库。
3. 新增调度器：`app/ingester/scheduler.py`
   - APScheduler 周期任务。
   - 可通过 `INGEST_INTERVAL_MINUTES` 配置间隔。
   - 调度异常保护，避免后台线程中断。
4. 新增手动触发接口：`POST /api/v1/ingest/sync`。

## 安装的依赖
本阶段未执行依赖安装命令（仅使用已声明依赖）：
- spacetrack
- apscheduler

## 当前可用功能
1. 支持手动触发 tracked 卫星的 TLE 同步。
2. 支持 `POST /satellites/{id}/track` 后立即触发单星补丁同步。
3. 支持调度器周期同步（默认 15 分钟）。

## 风险与后续
1. 真实 Space-Track 联调需要有效账号与网络访问。
2. 生产级限流建议迁移到持久化/分布式令牌桶。