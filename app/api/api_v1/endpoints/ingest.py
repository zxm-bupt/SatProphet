"""Ingestion control endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.ingester.service import sync_tracked_tles
from app.schemas.ingest import IngestSyncResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/sync", response_model=IngestSyncResponse)
async def trigger_sync(session: Session = Depends(get_session)) -> IngestSyncResponse:
    """Manually trigger tracked TLE synchronization."""
    result = sync_tracked_tles(session)
    return IngestSyncResponse(**result)
