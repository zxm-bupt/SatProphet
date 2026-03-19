# 测试报告（2026-03-17）

## 执行范围
- 依赖安装验证（Python + Frontend）
- 后端单元与接口测试
- 代码质量检查（Ruff / MyPy）
- 前端生产构建验证

## 环境与依赖安装
1. Python 环境：VirtualEnvironment，Python 3.14.3
2. 安装命令：`uv sync --all-groups`
   - 结果：成功（Resolved 61 packages, Audited 58 packages）
3. 前端安装命令：`cd web && npm install`
   - 结果：成功（added 112 packages，0 vulnerabilities）

## 测试用例明细
| 用例名称 | 前置条件 | 后置条件 | 预期成果 | 测试结果 |
|---|---|---|---|---|
| TC-API-001 健康检查接口 | 后端应用可启动；测试数据库可初始化 | 无持久化数据变更 | `GET /api/v1/health` 返回 200 与 `{\"status\":\"ok\"}` | 通过 |
| TC-API-002 tracked 列表过滤 | 数据库中存在 tracked 和非 tracked 卫星各 1 条 | 保留测试数据 | `GET /api/v1/satellites/tracked` 仅返回 tracked 卫星 | 通过 |
| TC-API-003 predict 缺失 TLE 场景 | 存在卫星记录但无 TLE 记录 | 保留测试数据 | `GET /api/v1/predict/{id}` 返回 404 | 通过 |
| TC-API-004 predict 成功场景 | 存在卫星记录及最新 TLE 记录 | 保留测试数据 | 返回 200，且经纬度落在合法区间 | 通过 |
| TC-INGEST-001 同步插入与去重 | 存在 tracked 卫星；FakeGateway 返回同一 epoch 两次 | 第二次不新增重复记录 | 首次 inserted=1，二次 skipped=1，总记录数不重复 | 通过 |
| TC-INGEST-002 空同步场景 | 无 tracked 卫星；FakeGateway 空返回 | 无数据变更 | 返回 `{tracked:0,fetched:0,inserted:0,skipped:0}` | 通过 |
| TC-BOOT-001 占位测试 | 测试框架可运行 | 无 | 占位测试成功执行，保证流水线可用 | 通过 |
| TC-QA-001 Ruff 静态检查 | Python 依赖已安装 | 无 | `uv run ruff check .` 无违规 | 通过 |
| TC-QA-002 MyPy 类型检查 | Python 依赖已安装 | 无 | `uv run mypy app` 无类型错误 | 通过 |
| TC-WEB-001 前端构建 | Node 依赖已安装 | 生成构建目录 `web/dist` | `npm run build` 成功产出前端静态资源 | 通过 |
| TC-DB-001 PostGIS 扩展可用性 | Podman 启动数据库容器；已执行迁移 | 无持久化变更 | `SELECT postgis_version()` 返回非空 | 通过 |
| TC-DB-002 核心表存在性 | Podman 启动数据库容器；已执行迁移 | 无持久化变更 | `satellite/tle_record/satellite_ground_track/alembic_version` 均存在 | 通过 |
| TC-DB-003 地理空间查询能力 | Podman 启动数据库容器；已执行迁移 | 清理测试插入数据 | `ST_DWithin` 在 `ground_point` 字段上可用且返回预期计数 | 通过 |

## 执行结果汇总
1. `uv run pytest -q`：7 passed in 0.58s
2. `uv run ruff check .`：All checks passed
3. `uv run mypy app`：Success: no issues found in 31 source files
4. 前端构建产物校验：`web/dist` 目录存在，包含 `index.html` 与 `assets/`
5. 数据库集成测试：`uv run pytest -q tests/test_db_postgis_integration.py -m db_integration`，结果 `3 passed`。

## 缺陷与修复记录
1. 初次 API 预测测试返回 422（时间参数拼接导致 `+00:00` 编码问题）。
   - 修复：改为 `client.get(..., params={"t": now})`。
   - 回归结果：相关用例通过。
2. 初次 MyPy 出现 SQLModel 表达式类型告警。
   - 修复：使用 `col(...)` 包装布尔过滤与排序表达式，补充 lifespan 返回类型。
   - 回归结果：MyPy 全量通过。
3. Podman 数据库联调已完成：使用 `postgis:16-3.5` 启动容器并完成迁移后，数据库集成测试通过。
   - 当前处理：保留 DB 不可达时自动 skip 机制，确保 CI 在无容器场景下仍可运行基础测试。

## 结论
本轮依赖安装与测试验收完成，后端测试、静态检查与前端构建均通过，满足当前阶段交付要求。

## 本次补充执行（Podman 数据库联调）
1. 使用 Podman 启动数据库：`podman compose up -d db`。
2. 容器健康状态：`satprophet-db Up (healthy)`。
3. 迁移执行：`PYTHONPATH=. uv run alembic upgrade head` 成功。
4. DB 集成测试：`3 passed`。
5. 全量测试回归：包含 DB 组在内的套件已再次执行并通过。
