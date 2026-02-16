"""Geospatial and text utility functions."""

from __future__ import annotations

import math
import re
from difflib import SequenceMatcher



def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two latitude/longitude points."""

    radius_m = 6_371_000
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi_1) * math.cos(phi_2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_m * c



def normalize_name(name: str) -> str:
    """Normalize shop name for deduplication comparisons."""

    cleaned = re.sub(r"[^a-z0-9 ]+", " ", (name or "").lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for suffix in (" cafe", " coffee", " juice", " smoothie", " co"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)].strip()
    return cleaned



def similarity(a: str, b: str) -> float:
    """Return string similarity score in [0, 1]."""

    return SequenceMatcher(None, a or "", b or "").ratio()
