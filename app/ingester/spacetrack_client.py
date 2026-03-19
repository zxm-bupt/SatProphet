"""Space-Track client wrapper with simple rate limiting."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any

from spacetrack import SpaceTrackClient

from app.core.config import settings


class _RateLimiter:
    """In-memory limiter for Space-Track usage windows."""

    def __init__(self, per_minute: int = 30, per_hour: int = 300) -> None:
        self._per_minute = per_minute
        self._per_hour = per_hour
        self._minute_hits: deque[datetime] = deque()
        self._hour_hits: deque[datetime] = deque()
        self._lock = Lock()

    def can_request(self) -> bool:
        """Return whether a request can be sent now."""
        with self._lock:
            now = datetime.now(timezone.utc)
            minute_floor = now - timedelta(minutes=1)
            hour_floor = now - timedelta(hours=1)

            while self._minute_hits and self._minute_hits[0] < minute_floor:
                self._minute_hits.popleft()
            while self._hour_hits and self._hour_hits[0] < hour_floor:
                self._hour_hits.popleft()

            return len(self._minute_hits) < self._per_minute and len(self._hour_hits) < self._per_hour

    def hit(self) -> None:
        """Record one API request."""
        with self._lock:
            now = datetime.now(timezone.utc)
            self._minute_hits.append(now)
            self._hour_hits.append(now)


class SpaceTrackGateway:
    """Fetches TLE records from Space-Track."""

    def __init__(self) -> None:
        self._client: SpaceTrackClient | None = None
        self._limiter = _RateLimiter()

    def _get_client(self) -> SpaceTrackClient:
        if self._client is None:
            if not settings.spacetrack_id or not settings.spacetrack_password:
                raise ValueError("Space-Track credentials are missing")
            self._client = SpaceTrackClient(identity=settings.spacetrack_id, password=settings.spacetrack_password)
        return self._client

    def fetch_latest_tle(self, norad_ids: list[int]) -> list[dict[str, Any]]:
        """Fetch latest TLE entries for the NORAD IDs.

        Args:
            norad_ids: NORAD catalog IDs.

        Returns:
            JSON-like payload returned by Space-Track.
        """
        if not norad_ids:
            return []
        if not self._limiter.can_request():
            raise RuntimeError("Space-Track rate limit budget exhausted in local limiter")

        client = self._get_client()
        self._limiter.hit()

        raw = client.tle_latest(
            norad_cat_id=norad_ids,
            ordinal=1,
            orderby="EPOCH desc",
            format="json",
        )

        if isinstance(raw, list):
            return [record for record in raw if isinstance(record, dict)]
        return []
