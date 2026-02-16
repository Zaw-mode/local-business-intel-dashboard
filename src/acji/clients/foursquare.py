"""Foursquare Places API client."""

from __future__ import annotations

from typing import Any

import requests


class FoursquareClient:
    """Client for retrieving places from Foursquare Places API."""

    BASE_URL = "https://api.foursquare.com/v3/places/search"

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
            "Authorization": self.api_key,
            "Accept": "application/json",
        }

        terms = ["coffee shop", "juice bar"]
        results: list[dict[str, Any]] = []

        for term in terms:
            params = {
                "ll": f"{lat},{lon}",
                "radius": radius_m,
                "query": term,
                "limit": 50,
                "sort": "DISTANCE",
                "fields": ",".join(
                    [
                        "fsq_id",
                        "name",
                        "categories",
                        "geocodes",
                        "location",
                        "distance",
                        "price",
                        "rating",
                        "stats",
                        "hours",
                        "website",
                    ]
                ),
            }
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            results.extend(payload.get("results", []))

        return results
