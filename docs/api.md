# SatProphet API 文档

Base URL: `http://<host>:8000/api/v1`

---

## 1. 健康检查

### GET /health

检查服务运行状态。

**请求参数**: 无

**响应示例** (200):
```json
{
  "status": "ok"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 服务状态，正常为 `"ok"` |

---

## 2. 卫星管理

### GET /satellites

获取数据库中的全部卫星（包含 tracked 与非 tracked）。

**请求参数**: 无

**响应示例** (200):
```json
[
  {
    "id": 1,
    "norad_id": 25544,
    "name": "ISS (ZARYA)",
    "is_tracked": true,
    "updated_at": "2026-04-13T10:05:29.859460Z"
  },
  {
    "id": 2,
    "norad_id": 64050,
    "name": "BUPT-3",
    "is_tracked": false,
    "updated_at": "2026-04-15T04:00:00.000000Z"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 数据库主键 |
| norad_id | int | NORAD 编号 |
| name | string | 卫星名称 |
| is_tracked | bool | 是否正在追踪 |
| updated_at | string (ISO8601) | 最后更新时间 |

---

### POST /satellites

新增一颗卫星记录。

**请求体**:
```json
{
  "norad_id": 64049,
  "name": "BUPT-2",
  "is_tracked": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| norad_id | int | 是 | NORAD 编号（唯一） |
| name | string | 是 | 卫星名称 |
| is_tracked | bool | 否 | 是否开启追踪，默认 `false` |

**响应示例** (201):
```json
{
  "id": 10,
  "norad_id": 64049,
  "name": "BUPT-2",
  "is_tracked": true,
  "updated_at": "2026-04-15T04:00:00.000000Z"
}
```

**错误响应** (409):
```json
{
  "detail": "Satellite with NORAD 64049 already exists"
}
```

---

### GET /satellites/tracked

获取当前所有已追踪的卫星列表。

**请求参数**: 无

**响应示例** (200):
```json
[
  {
    "id": 1,
    "norad_id": 25544,
    "name": "ISS (ZARYA)",
    "is_tracked": true,
    "updated_at": "2026-04-13T10:05:29.859460Z"
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 数据库主键 |
| norad_id | int | NORAD 编号 |
| name | string | 卫星名称 |
| is_tracked | bool | 是否正在追踪 |
| updated_at | string (ISO8601) | 最后更新时间 |

---

### POST /satellites/{satellite_id}/track

设置卫星追踪状态。开启追踪时会自动触发一次 TLE 同步。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| satellite_id | int | 是 | 卫星数据库 ID |

**请求体**:
```json
{
  "enable": true
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| enable | bool | 是 | `true` 开启追踪，`false` 关闭追踪 |

**响应示例** (200):
```json
{
  "id": 1,
  "norad_id": 25544,
  "is_tracked": true,
  "patch": {
    "fetched": 1,
    "inserted": 1,
    "skipped": 0
  },
  "patch_error": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 卫星数据库 ID |
| norad_id | int | NORAD 编号 |
| is_tracked | bool | 当前追踪状态 |
| patch | object \| null | TLE 同步结果（仅开启追踪时返回） |
| patch.fetched | int | 从 Space-Track 获取的 TLE 条数 |
| patch.inserted | int | 新插入的 TLE 条数 |
| patch.skipped | int | 因去重跳过的条数 |
| patch_error | string \| null | 同步错误信息，成功时为 `null` |

**错误响应** (404):
```json
{
  "detail": "Satellite not found"
}
```

---

## 3. TLE 数据同步

### POST /ingest/sync

手动触发所有已追踪卫星的 TLE 数据同步。从 Space-Track.org 拉取最新 TLE 并入库。

**请求参数**: 无

**响应示例** (200):
```json
{
  "tracked": 3,
  "fetched": 3,
  "inserted": 3,
  "skipped": 0
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| tracked | int | 当前追踪的卫星总数 |
| fetched | int | 从 Space-Track 获取的 TLE 条数 |
| inserted | int | 新插入数据库的 TLE 条数 |
| skipped | int | 因去重（相同 satellite_id + epoch）跳过的条数 |

---

## 4. 轨道预测

### GET /predict/{satellite_id}

预测指定卫星在给定时刻的地理位置（WGS84 坐标）。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| satellite_id | int | 是 | 卫星数据库 ID |

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| t | string (ISO8601) | 是 | 预测时间点，如 `2026-04-13T12:00:00Z` |

**请求示例**:
```
GET /api/v1/predict/10?t=2026-04-13T12:00:00Z
```

**响应示例** (200):
```json
{
  "satellite_id": 10,
  "latitude_deg": 49.843,
  "longitude_deg": -6.813,
  "altitude_km": 513.564,
  "timestamp_utc": "2026-04-13T12:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| satellite_id | int | 卫星数据库 ID |
| latitude_deg | float | 纬度（度），范围 -90 ~ 90 |
| longitude_deg | float | 经度（度），范围 -180 ~ 180 |
| altitude_km | float | 海拔高度（千米） |
| timestamp_utc | string (ISO8601) | 预测时间（UTC） |

**错误响应** (404):
```json
{
  "detail": "TLE not found for satellite"
}
```

---

## 通用错误格式

所有错误响应遵循 FastAPI 默认格式：

```json
{
  "detail": "错误描述信息"
}
```

| HTTP 状态码 | 说明 |
|-------------|------|
| 201 | 创建成功 |
| 200 | 请求成功 |
| 409 | 资源冲突（如 NORAD 已存在） |
| 404 | 资源未找到（卫星不存在或无 TLE 数据） |
| 422 | 请求参数校验失败 |
| 500 | 服务器内部错误 |
