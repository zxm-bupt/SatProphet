# SatProphet API Curl 测试命令

以下命令基于本地后端地址：`http://127.0.0.1:8000/api/v1`。

## 1) 查询所有卫星

```bash
curl -sS http://127.0.0.1:8000/api/v1/satellites
```

## 2) 增加卫星

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/satellites \
  -H 'Content-Type: application/json' \
  -d '{"norad_id":64049,"name":"BUPT-2","is_tracked":false}'
```

## 3) 查询追踪卫星

```bash
curl -sS http://127.0.0.1:8000/api/v1/satellites/tracked
```

## 4) 开启卫星追踪

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/satellites/13/track \
  -H 'Content-Type: application/json' \
  -d '{"enable":true}'
```

## 5) 同步 TLE

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/ingest/sync
```

## 6) 查询卫星位置

```bash
curl -sS "http://127.0.0.1:8000/api/v1/predict/13?t=2026-04-15T04:25:39Z"
```

> 说明：`/track` 与 `/predict` 示例中的 `13` 为卫星数据库 `id`，请先通过
> `GET /api/v1/satellites` 查询实际 `id` 后替换。
