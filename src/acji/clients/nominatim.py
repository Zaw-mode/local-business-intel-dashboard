"""OpenStreetMap Nominatim search API client."""

from __future__ import annotations

import math
import time
from typing import Any

import requests


class NominatimClient:
    """Client for retrieving nearby coffee/juice listings from Nominatim."""

    def __init__(
        self,
        endpoint: str = "https://nominatim.openstreetmap.org/search",
        user_agent: str = "ACJI/0.1 (local development)",
        timeout_seconds: int = 30,
        request_delay_seconds: float = 1.0,
    ) -> None:
        self.endpoint = endpoint
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.request_delay_seconds = max(0.0, request_delay_seconds)

    @staticmethod
    def _build_viewbox(lat: float, lon: float, radius_m: int) -> str:
        # Approximate conversion from meters to lat/lon degrees.
        lat_delta = radius_m / 111_320
        cos_lat = max(0.01, math.cos(math.radians(lat)))
        lon_delta = radius_m / (111_320 * cos_lat)

        left = lon - lon_delta
        right = lon + lon_delta
        top = lat + lat_delta
        bottom = lat - lat_delta
        return f"{left},{top},{right},{bottom}"

    def fetch_places(self, lat: float, lon: float, radius_m: int) -> list[dict[str, Any]]:
        """Fetch nearby places using free Nominatim queries."""

        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        viewbox = self._build_viewbox(lat, lon, radius_m)

        terms = ["coffee shop", "juice bar", "smoothie"]
        all_results: list[dict[str, Any]] = []

        for idx, term in enumerate(terms):
            params = {
                "q": term,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 50,
                "bounded": 1,
                "viewbox": viewbox,
                "countrycodes": "us",
            }
            response = requests.get(
                self.endpoint,
                headers=headers,
                params=params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()

            records = response.json()
            if isinstance(records, list):
                for record in records:
                    record["_query_term"] = term
                all_results.extend(records)

            if idx < len(terms) - 1 and self.request_delay_seconds > 0:
                time.sleep(self.request_delay_seconds)

        deduplicated: dict[str, dict[str, Any]] = {}
        for item in all_results:
            place_id = str(item.get("place_id") or item.get("osm_id") or id(item))
            deduplicated[place_id] = item

        return list(deduplicated.values())
