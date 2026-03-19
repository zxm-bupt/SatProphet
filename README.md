# SatProphet

SatProphet is a satellite tracking and prediction system based on FastAPI, PostGIS, and Cesium.

## Phase 0 Scope
- Backend project skeleton with FastAPI app and health endpoint.
- Frontend shell with Vite + React and Cesium container placeholder.
- Dependency management baseline with `uv`.

## Prerequisites
- Python 3.12+
- Node.js 20+
- Podman + podman-compose (recommended)

## Deployment And Usage Guide
- See [docs/deployment-and-usage.md](docs/deployment-and-usage.md)

## Local Setup
```bash
uv sync --all-groups
```

## Run Backend
```bash
uv run uvicorn app.main:app --reload
```

## Core API Endpoints
- `GET /api/v1/health`
- `GET /api/v1/satellites/tracked`
- `POST /api/v1/satellites/{id}/track`
- `GET /api/v1/predict/{id}?t=<ISO8601>`
- `POST /api/v1/ingest/sync`

## Run Database (PostGIS)
```bash
podman compose up -d db
```

## Run Migrations
```bash
PYTHONPATH=. uv run alembic upgrade head
```

## Run Frontend
```bash
cd web
npm install
npm run dev
```

Frontend expects backend at `http://localhost:8000/api/v1` by default.
You can override with `VITE_API_BASE`.

## Environment Variables
Copy `.env.example` to `.env` and fill credentials.

```bash
cp .env.example .env
```

Required Space-Track credentials:
- `SPACETRACK_ID`
- `SPACETRACK_PASSWORD`

## Quality Commands
```bash
uv run ruff check .
uv run mypy app
uv run pytest
```
