"""Ingestion API schemas."""

from pydantic import BaseModel


class IngestSyncResponse(BaseModel):
    """Manual sync response."""

    tracked: int
    fetched: int
    inserted: int
    skipped: int
