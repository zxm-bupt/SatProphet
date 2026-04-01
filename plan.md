## Plan: SatProphet MVP 后续开发（下一阶段）

目标：在已完成 MVP 闭环（ingest -> predict -> visualize）基础上，进入“可持续开发”阶段，优先补齐稳定性、可观测性、精度验证与可交付能力。

---

## 1. 当前项目组成与现状

### 1.1 后端（FastAPI）
1. 接口层：`app/api/api_v1/endpoints/` 已提供 health、tracked、track、predict、ingest/sync。
2. 数据层：`app/models/` + `app/crud/` + Alembic 已具备卫星/TLE/地影点基础模型与迁移。
3. 同步层：`app/ingester/` 已接入 Space-Track、支持限流、去重、手动与定时同步。
4. 计算层：`app/engine/` 已通过 Skyfield 路径输出 WGS84 经纬高，astroz 保留集成入口。

### 1.2 前端（React + Cesium）
1. `web/src/App.tsx` 已具备卫星选择、时间选择、预测触发与结果展示。
2. `web/src/viewer/CesiumViewer.tsx` 已支持点位渲染与相机飞行。
3. 已具备 TLE 老化提示（>3天）。

### 1.3 工程化与测试
1. 已有 pytest、ruff、mypy 基线命令。
2. 已有 API/ingester/DB 集成测试，但覆盖仍偏核心 happy path。
3. 当前凭据管理仍是本地 `.env`，生产化安全能力未落地。

结论：MVP 功能闭环已完成，下一阶段应从“能跑”升级为“稳定、可观测、可验证、可发布”。

---

## 2. 下一阶段开发范围（Phase 7）

### 2.1 目标
1. 提升系统在真实网络与数据波动下的鲁棒性。
2. 建立可观测与告警能力，支持问题定位。
3. 补齐预测精度验证与回归体系。
4. 形成 Beta 可交付基线（不是最终生产版）。

### 2.2 里程碑与任务

Milestone A：稳定性与容错（优先级 P0）
1. 为 Space-Track 拉取增加可配置重试策略（指数退避 + 最大重试次数）。
2. 细化 ingest 错误分类：认证失败、限流耗尽、网络超时、上游返回异常。
3. 为 `POST /ingest/sync` 与 `POST /satellites/{id}/track` 增加可追踪任务结果字段（成功数、失败数、失败原因聚合）。
4. 增加调度任务重入保护与执行耗时记录。

Milestone B：可观测性（优先级 P0）
1. 引入结构化日志（JSON 或 key-value），统一请求 ID / 任务 ID。
2. 增加健康扩展接口（建议 `GET /api/v1/health/detail`）：
	- DB 可连通性。
	- 最近一次 ingest 时间与结果。
	- Space-Track 凭据是否配置（不暴露敏感值）。
3. 增加最小指标：ingest 成功率、预测请求耗时、TLE 新鲜度分布。

Milestone C：预测能力增强（优先级 P1）
1. 新增轨迹预测接口（建议）：
	- `GET /api/v1/predict/{id}/trajectory?start=&end=&step_seconds=`。
2. 增加 TLE 状态接口（建议）：
	- `GET /api/v1/satellites/{id}/tle-status`（返回最新 epoch、age_hours、stale 标记）。
3. 保持现有单点预测接口兼容，不破坏前端已接入路径。

Milestone D：测试与质量门禁（优先级 P0）
1. 为 ingest 增加失败场景测试：凭据错误、超时、限流、上游空数据。
2. 为 predict 增加边界测试：无效时间格式、极端时间跨度、satellite 不存在。
3. 新增端到端主链路测试：track -> patch sync -> predict。
4. 增加前端最小集成测试（API 错误展示、空列表、老化提示）。

Milestone E：安全与交付（优先级 P1）
1. 将 `.env.example` 明确为占位值，不允许真实凭据进入仓库。
2. 增加凭据泄露防护（pre-commit 或 CI 扫描）。
3. 输出 Beta 发布说明：已知限制、回滚步骤、故障处置手册。

---

## 3. 交付物清单
1. 新增/更新 API 文档（含新接口示例请求与响应）。
2. 可观测性文档：日志字段说明、健康检查说明、指标定义。
3. 测试报告：覆盖率与关键失败场景结果。
4. Beta 运行手册：部署、排障、回滚。

---

## 4. 验收标准（DoD）
1. 在无人工干预下，定时 ingest 连续运行 24 小时无崩溃。
2. 上游异常（超时/认证失败）不会导致服务不可用，错误可追踪。
3. 新增接口通过测试，且旧接口保持兼容。
4. `uv run pytest -q`、`uv run ruff check .`、`uv run mypy app` 全通过。
5. 前端可展示预测失败原因与 TLE 时效状态。

---

## 5. 建议开发顺序（2-3 周）
1. 第 1 周：Milestone A + B（稳定性、可观测性先落地）。
2. 第 2 周：Milestone C + D（接口增强与测试补齐并行）。
3. 第 3 周：Milestone E（安全与交付），完成 Beta 冻结与验收。

---

## 6. 风险与前置条件
1. 需要稳定的 Space-Track 测试账号与网络访问。
2. 需要明确精度验收样本集（卫星 ID、时间点、参考来源）。
3. 若计划近期公网部署，应提前决定鉴权方案（API Key/JWT）。
