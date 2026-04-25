"""City -> (lat, lng) lookup used by the demo/seed pipelines.

Keeps lat/lng derivation out of route handlers so every ingestion path can
populate ``incidents.map_lat`` / ``incidents.map_lng`` consistently. The
frontend threat map reads these columns; when NULL, markers fall back to
the first recognized city in ``map_region``.
"""

from __future__ import annotations

from typing import Optional, Tuple


# Canonical, roughly-centered coordinates for the demo cities.
CITY_COORDS: dict[str, Tuple[float, float]] = {
    "singapore": (1.3521, 103.8198),
    "london": (51.5074, -0.1278),
    "dubai": (25.2048, 55.2708),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "berlin": (52.5200, 13.4050),
    "cairo": (30.0444, 31.2357),
    "nairobi": (-1.2921, 36.8219),
    "lisbon": (38.7223, -9.1393),
    "são paulo": (-23.5505, -46.6333),
    "sao paulo": (-23.5505, -46.6333),
    "seoul": (37.5665, 126.9780),
    "tokyo": (35.6762, 139.6503),
    "jakarta": (-6.2088, 106.8456),
    "manila": (14.5995, 120.9842),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new york": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "paris": (48.8566, 2.3522),
    "madrid": (40.4168, -3.7038),
    "sydney": (-33.8688, 151.2093),
}


def coords_for_region(region: Optional[str]) -> Optional[Tuple[float, float]]:
    """Resolve the first recognizable city in a region string.

    Accepts free-form values like ``"Singapore -> London -> Dubai"`` — we
    anchor the incident marker on the originating city (first hop) because
    that is where the reupload surfaced. Returns ``None`` when nothing
    matches so callers can decide whether to store NULL or a default.
    """

    if not region:
        return None
    # Split on arrow chains so "Singapore -> London -> Dubai" -> "Singapore".
    parts = [p.strip() for p in region.replace("→", "->").split("->") if p.strip()]
    for part in parts + [region]:
        key = part.strip().lower()
        if key in CITY_COORDS:
            return CITY_COORDS[key]
    return None
