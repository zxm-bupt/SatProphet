# Phase 6 开发报告

## 阶段目标
补齐核心测试与交付文档，完成可回归的 MVP 基线。

## 本阶段完成内容
1. 新增后端 API 测试：`tests/test_api_endpoints.py`
   - 健康检查。
   - tracked 列表。
   - predict 缺失 TLE 场景（404）。
   - predict 成功场景。
2. 新增 ingester 服务测试：`tests/test_ingester_service.py`
   - 增量同步插入。
   - Epoch 去重跳过。
3. 更新 `README.md`
   - 增加核心 API 说明。
   - 增加前后端联调说明与必要环境变量。

## 安装的依赖
1. Python 依赖安装：`uv sync --all-groups`
2. 前端依赖安装：`cd web && npm install`

## 当前可用功能
1. 代码层面已具备端到端主链路（同步 -> 预测 -> 可视化）。
2. 测试用例已覆盖关键后端路径并完成执行验证。

## 已执行验证
1. `uv run pytest -q`：7 passed。
2. `uv run ruff check .`：All checks passed。
3. `uv run mypy app`：Success, no issues found。
4. `cd web && npm run build`：构建产物存在于 `web/dist`。