"""Health-check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
