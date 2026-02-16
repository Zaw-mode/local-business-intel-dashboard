"""OpenStreetMap Overpass API client."""

from __future__ import annotations

from typing import Any

import requests


class OverpassClient:
    """Client for retrieving Austin coffee/juice places from OSM Overpass."""

    def __init__(self, endpoint: str, timeout_seconds: int = 60) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def fetch_places(self, lat: float, lon: float, radius_m: int) -> list[dict[str, Any]]:
        """Fetch OSM elements matching cafe/coffee/juice categories."""

        query = f"""
        [out:json][timeout:60];
        (
          node["amenity"~"cafe|juice_bar"](around:{radius_m},{lat},{lon});
          way["amenity"~"cafe|juice_bar"](around:{radius_m},{lat},{lon});
          relation["amenity"~"cafe|juice_bar"](around:{radius_m},{lat},{lon});
          node["shop"~"coffee"](around:{radius_m},{lat},{lon});
          way["shop"~"coffee"](around:{radius_m},{lat},{lon});
          relation["shop"~"coffee"](around:{radius_m},{lat},{lon});
        );
        out center tags;
        """.strip()

        response = requests.post(
            self.endpoint,
            data={"data": query},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("elements", [])
