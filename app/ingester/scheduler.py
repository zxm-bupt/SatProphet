"""Scheduler integration for ingestion tasks."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.database import SessionLocal
from app.ingester.service import sync_tracked_tles

scheduler = BackgroundScheduler(timezone="UTC")


def run_scheduled_sync() -> None:
    """Execute one scheduled sync run."""
    try:
        with SessionLocal() as session:
            sync_tracked_tles(session)
    except Exception:
        # Best-effort scheduler path. Endpoint-triggered manual sync surfaces errors explicitly.
        return


def start_scheduler() -> None:
    """Start periodic TLE synchronization."""
    if scheduler.running:
        return
    scheduler.add_job(
        run_scheduled_sync,
        "interval",
        minutes=settings.ingest_interval_minutes,
        id="tle_sync",
        replace_existing=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    """Stop scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
