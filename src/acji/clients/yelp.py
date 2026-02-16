"""Yelp Fusion API client."""

from __future__ import annotations

from typing import Any

import requests


class YelpClient:
    """Client for retrieving places from Yelp Fusion API."""

    BASE_URL = "https://api.yelp.com/v3/businesses/search"

    def __init__(self, api_key: str, timeout_seconds: int = 30) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def fetch_places(self, lat: float, lon: float, radius_m: int) -> list[dict[str, Any]]:
        """Fetch nearby coffee/juice places.

        Returns an empty list if no API key is configured.
        """

        if not self.api_key:
            return []

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        offset = 0
        limit = 50
        all_results: list[dict[str, Any]] = []

        while True:
            params = {
                "latitude": lat,
                "longitude": lon,
                "radius": min(radius_m, 40000),
                "categories": "coffee,juicebars,smoothies",
                "limit": limit,
                "offset": offset,
                "sort_by": "best_match",
            }
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            businesses = payload.get("businesses", [])
            all_results.extend(businesses)

            if len(businesses) < limit or offset + limit >= 200:
                break
            offset += limit

        return all_results
