"""API v1 router registration."""

from fastapi import APIRouter

from app.api.api_v1.endpoints.health import router as health_router
from app.api.api_v1.endpoints.ingest import router as ingest_router
from app.api.api_v1.endpoints.predict import router as predict_router
from app.api.api_v1.endpoints.satellites import router as satellites_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(satellites_router)
api_router.include_router(predict_router)
api_router.include_router(ingest_router)
