from __future__ import annotations

import json
import time
from dataclasses import dataclass

import requests


@dataclass
class GeoPoint:
    lat: float
    lng: float
    display_name: str | None = None


def geocode_nominatim(query: str, *, user_agent: str = "local-business-intel-dashboard/1.0", timeout_s: int = 20) -> GeoPoint:
    """Geocode a free-form place string (e.g. "Austin, TX") using OSM Nominatim.

    No API key required.

    Note: Nominatim has usage policies; we keep requests low and cache in caller if needed.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": user_agent}

    # be polite
    time.sleep(1.0)

    r = requests.get(url, params=params, headers=headers, timeout=timeout_s)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise RuntimeError(f"Geocode not found for: {query}")

    top = data[0]
    return GeoPoint(lat=float(top["lat"]), lng=float(top["lon"]), display_name=top.get("display_name"))
