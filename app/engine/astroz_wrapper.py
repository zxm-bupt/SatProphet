"""Astroz wrapper.

The implementation keeps astroz optional during development bootstrap:
if astroz is unavailable, prediction falls back to Skyfield SGP4 path.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class TemePosition:
    """TEME coordinates in km and km/s."""

    x_km: float
    y_km: float
    z_km: float
    vx_km_s: float
    vy_km_s: float
    vz_km_s: float


class AstrozPropagator:
    """Thin abstraction for astroz propagation."""

    def __init__(self) -> None:
        self._available = False
        try:
            import astroz  # noqa: F401

            self._available = True
        except Exception:
            self._available = False

    @property
    def available(self) -> bool:
        """Return whether astroz import succeeded."""
        return self._available

    def propagate(self, line1: str, line2: str, when: datetime) -> TemePosition | None:
        """Propagate one satellite state in TEME coordinates.

        Returns None when astroz is unavailable. In that case callers should
        use the Skyfield fallback path to keep MVP functional.
        """
        if not self._available:
            return None

        # TODO: Wire to astroz API once runtime dependency is installed and validated.
        _ = (line1, line2)
        ts = when.astimezone(timezone.utc).timestamp()
        raise NotImplementedError(f"Astroz runtime propagation is pending integration. ts={ts}")
