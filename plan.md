## Plan: SatProphet MVP 分阶段开发

目标是在“后端+最小前端”范围内，先打通从 Space-Track 拉取 TLE 到高精度预测与 Cesium 展示的闭环。采用 uv、Alembic、astroz+Skyfield、本地 .env 凭据管理，并以可独立验收的里程碑推进。

**Steps**

Phase 0: 项目初始化与基线约束（阻塞后续全部阶段）
1. 创建 Python 工程骨架与依赖管理，确定 uv 工作流、代码格式与测试工具链，补充最小 README（开发启动、测试、环境变量说明）。
2. 建立后端目录骨架与配置系统：配置加载、数据库连接、基础 FastAPI 应用入口、健康检查接口。
3. 建立前端 Vite + React + Cesium 最小骨架（仅壳层页面与地图初始化，不做复杂 UI）。

Phase 1: 持久化与数据模型（依赖 Phase 0）
4. 初始化 PostgreSQL 16 + PostGIS 容器编排与本地联调网络配置。
5. 设计核心数据模型（卫星、TLE 历史、跟踪状态），创建 Alembic 初始迁移，确保空间字段与必要索引到位。
7. 建立 CRUD 最小集合（tracked 列表读取、跟踪状态更新、按卫星读取最新 TLE）。
   
Phase 2: Ingester 与数据同步（依赖 Phase 1）
8.  实现 Space-Track 客户端（认证、重试、限流、错误分类），读取 .env 凭据。
9.  实现增量同步逻辑：仅同步 is_tracked=TRUE，按 Epoch 去重并写入历史。
10. 接入 APScheduler：提供手动触发与定时任务两种入口，支持首次补丁更新。

Phase 3: 轨道计算引擎（依赖 Phase 1，可与 Phase 2 并行后半段）
11. 封装 astroz 推演接口与批量传播调用。
12. 实现 Skyfield 坐标转换（TEME -> WGS84），并定义统一输出（经纬高+时间戳）。
13. 建立高精度验证基线：选取样本卫星与时间点，记录误差计算方法与阈值。

Phase 4: API 业务闭环（依赖 Phase 2 + Phase 3）
14. 实现 GET /satellites/tracked。
15. 实现 POST /satellites/{id}/track，更新 is_tracked 后触发一次 TLE 更新补丁。
18. 实现 GET /predict/{id}?t=timestamp，返回指定时刻经纬高。
19. 完成 Pydantic v2 输入输出模型、统一错误码与异常处理。

Phase 5: 最小前端联调（依赖 Phase 4）
20. 实现前端 API 封装与基础状态管理，拉取 tracked 卫星并展示。
21. 在 Cesium 上渲染动态点位/轨迹，展示 TLE 时效性提示（超过 3 天告警）。
23. 完成最小交互：选择卫星、查看当前位置与预测时间点结果。

Phase 6: 测试、验收与交付（依赖全部前序）
24. 后端单元测试：模型/CRUD/服务层；接口测试覆盖 3 个核心端点。
26. 引擎精度测试：固定样本回归，防止算法或转换回归。
27. 前端联调测试：接口异常、空数据、TLE 过期提示。
28. 交付文档：运行手册、环境变量模板、已知限制与下一阶段路线。

**Relevant files**
- /home/euler/workspace/SatProphet/.github/copilot-instructions.md — 作为当前唯一已存在的架构与规范基线。
- 规划新增目录：/home/euler/workspace/SatProphet/app, /home/euler/workspace/SatProphet/web, /home/euler/workspace/SatProphet/migrations, /home/euler/workspace/SatProphet/tests。
- 规划新增关键文件：/home/euler/workspace/SatProphet/pyproject.toml, /home/euler/workspace/SatProphet/docker-compose.yml, /home/euler/workspace/SatProphet/.env.example。

**Verification**
1. 环境验证：容器成功启动 PostgreSQL+PostGIS，后端可连通数据库并通过健康检查。
2. 数据验证：手动触发一次 TLE 同步后，数据库可见新增 TLE 历史且 Epoch 去重生效。
3. 计算验证：给定卫星与时间点返回稳定经纬高结果，误差不超过已确认阈值。
4. API 验证：3 个核心接口在正常与异常输入下均返回预期结构。
5. 前端验证：Cesium 正常渲染，tracked 列表可交互，TLE 超期提示可触发。
6. 回归验证：测试套件通过，关键路径（track -> ingest patch -> predict）端到端通过。

**Decisions**
- 已确认包含范围：后端 + 最小前端。
- 已确认工具链：uv + FastAPI + Pydantic v2 + Alembic + PostgreSQL16/PostGIS。
- 已确认精度路线：astroz + Skyfield（高精度优先）。
- 已确认安全边界：MVP 暂不启用 API 鉴权，仅本地/内网验证。
- 已确认凭据方式：本地 .env。

**Further Considerations**
1. 精度阈值数值尚未给出（仅确认“高精度优先”），实施前需定义可验收的误差门限与样本集。
2. Space-Track 真实账号接入需要你提供变量名与注入方式约定（例如 SPACETRACK_ID / SPACETRACK_PASSWORD）。
3. 里程碑建议每阶段结束都做一次演示与冻结，避免并行开发导致接口频繁变更。
