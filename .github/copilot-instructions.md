# 1. 整体模块设计 (System Modules)
系统分为五个核心功能模块，通过解耦确保高性能计算与数据的实时性。

|模块名称	|核心功能	|交互关系|
|--- | --- | --- |
|1. TLE 接收器 (Ingester)|	从 Space-Track 抓取最新 TLE 数据|	写入数据库 (Persistence)|
|2. 持久化层 (Persistence)|	存储卫星元数据、历史 TLE 及跟踪状态|	为 API 和 Ingester 提供数据支撑|
|3. 轨道计算引擎 (Engine)|	使用 astroz 进行高性能 SGP4/SDP4 外推 |被 API 调用，进行实时或批量预测|
|4. REST API (FastAPI)|	提供卫星检索、位置查询及跟踪配置接口|	连接前端与后端计算逻辑|
|5. 可视化前端 (Visualizer)|	基于 CesiumJS 的 3D 数字地球动态展示|	从 API 获取坐标并渲染轨迹|

基于 FastAPI 大型应用最佳实践，系统采用以下分层结构：
```bash
SatProphet/
├── app/                        # 后端核心代码 (FastAPI)
│   ├── api/                    # 路由与接口层
│   │   ├── api_v1/             # 版本化接口
│   │   │   ├── endpoints/      # 具体业务路由 (satellites.py, tracking.py)
│   │   │   └── api.py          # 路由汇总
│   │   └── deps.py             # 依赖注入 (DB session, auth)
│   ├── core/                   # 全局配置与系统级代码
│   │   ├── config.py           # 环境变量与 Space-Track 凭据
│   │   └── database.py         # SQLAlchemy/PostGIS 连接初始化
│   ├── engine/                 # 轨道计算引擎模块
│   │   ├── astroz_wrapper.py   # astroz 算法库封装 
│   │   └── coordinate_conv.py  # TEME 到 WGS84 坐标转换逻辑 
│   ├── ingester/               # TLE 同步与数据抓取模块
│   │   ├── spacetrack_client.py# Space-Track API 交互封装 
│   │   └── scheduler.py        # 基于 APScheduler 的定时任务
│   ├── models/                 # SQLModel/SQLAlchemy 数据库模型
│   ├── schemas/                # Pydantic 数据验证模型
│   ├── crud/                   # 数据库增删改查逻辑
│   └── main.py                 # FastAPI 应用入口
├── web/                        # 前端展示代码 (React/Vite)
│   ├── src/
│   │   ├── components/         # UI 组件 (侧边栏, 配置面板)
│   │   ├── viewer/             # CesiumJS 地球渲染引擎逻辑
│   │   └── api/                # 前端接口请求封装
│   └── public/                 # 静态资源 (卫星 3D 模型等)
├── migrations/                 # Alembic 数据库迁移文件
├── tests/                      # 单元测试与计算精度验证
├── docker/                     # Dockerfile 与容器配置
├── docker-compose.yml          # 一键部署配置 (PostgreSQL + PostGIS)
└── pyproject.toml              # 依赖管理 (Poetry/Pip)
```

# 2. 模块框架与技术细节
## 2.1 TLE 接收器 (Ingester)

* 技术框架: python-spacetrack + apscheduler。
* 实现细节:
  * 使用官方库处理 API 会话及自动重试。
  * 限流管理: 严格遵守 30 次请求/分钟，300 次/小时的限制 。
  * 增量更新: 仅抓取 is_tracked=TRUE 的卫星，并根据历元（Epoch）时间戳进行去重 。

## 2.2 持久化层 (Persistence)

* 技术框架: PostgreSQL 16 + PostGIS 扩展 + SQLModel (ORM)。
* 空间存储:
  * 使用 GEOGRAPHY(POINT, 4326) 存储卫星地影点。
  * 利用 PostGIS 的 ST_DWithin 进行快速地理围栏判断（如卫星是否进入特定地面站可见范围）。

## 2.3 轨道计算引擎 (Engine)

* 技术框架: astroz (Zig/SIMD 加速) + Skyfield (坐标转换)。
* 计算性能:
  * 利用 astroz 的 SatrecArray.sgp4 并行传播能力，实现每秒千万次级的坐标推算。
  * 坐标转换: astroz 输出 TEME 惯性系坐标，需经由 Skyfield 或 Orekit 转换至 WGS84（地固系）以供 PostGIS 和 CesiumJS 使用。

## 2.4 接口层 (FastAPI)

* 技术框架: FastAPI + Pydantic v2 + Uvicorn。
* 核心功能:
  * GET /satellites/tracked: 返回正在实时跟踪的卫星列表。
  * POST /satellites/{id}/track: 卫星跟踪配置函数。修改数据库中的 is_tracked 标志，并立即触发一次 TLE 更新补丁。
  * GET /predict/{id}?t={timestamp}: 返回该时间点的坐标（经纬高）。

## 2.5 可视化前端 (Visualizer)

* 技术框架: CesiumJS + React + Vite。
* 展示逻辑:
  * 加载 CzmlDataSource 实现卫星动态点位渲染。
  * 实时计算并显示“TLE 时效性”，若 TLE 超过 3 天则在 UI 提示预测精度下降。
# 3. 代码规范 (Google Style)
为了确保 Gemini CLI 生成的代码整洁、易于维护且具备工业级质量，请遵循以下规范：

## 3.1 Python 规范 (符合 Google Python Style Guide)

* 命名: 函数名、变量名使用 snake_case；类名使用 PascalCase；常量使用 UPPER_SNAKE_CASE。
* 类型提示: 必须为所有函数参数和返回值提供 Type Hints。
* 文档注释: 使用 Google Style Docstrings。

```Python
def configure_satellite_tracking(norad_id: int, enable: bool) -> bool:
    """配置特定卫星的跟踪状态。

    Args:
        norad_id: NORAD 目录编号。
        enable: 是否启用实时跟踪。

    Returns:
        操作是否成功。
    """
    pass
```
* 异步编程: API 与 I/O 操作必须使用 async / await 以最大化利用 FastAPI 的并发性能。

## 3.2 SQL/PostGIS 规范

* 关键字: SQL 关键字（SELECT, FROM, JOIN）必须全大写。

* 空间函数: 优先使用索引化的空间函数（如 ST_Intersects），避免在大表上进行全表扫描。

