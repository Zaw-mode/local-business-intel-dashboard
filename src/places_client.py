from __future__ import annotations

import os
import time
import platform
import requests

PLACES_BASE = "https://places.googleapis.com/v1"


def _get_user_env_windows(name: str) -> str | None:
    """Read a Windows *User* environment variable (HKCU\\Environment).

    This is important because scheduled/daemonized processes sometimes don't
    inherit fresh `setx` values into their process env.
    """
    try:
        import winreg  # type: ignore

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as k:
            val, _typ = winreg.QueryValueEx(k, name)
            return str(val) if val else None
    except Exception:
        return None


class PlacesClient:
    def __init__(self, api_key: str | None = None, timeout_s: int = 30):
        self.api_key = api_key or os.environ.get("OPENCLAW_GOOGLE_PLACES_API_KEY")
        if not self.api_key and platform.system().lower().startswith("win"):
            self.api_key = _get_user_env_windows("OPENCLAW_GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing OPENCLAW_GOOGLE_PLACES_API_KEY")
        self.timeout_s = timeout_s

    def _headers(self, field_mask: str | None = None) -> dict:
        h = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        if field_mask:
            h["X-Goog-FieldMask"] = field_mask
        return h

    def search_text(self, text_query: str, lat: float, lng: float, radius_m: int, limit: int = 20) -> list[dict]:
        url = f"{PLACES_BASE}/places:searchText"
        payload = {
            "textQuery": text_query,
            "locationBias": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius_m,
                }
            },
            "pageSize": min(limit, 20),
            # languageCode can be added if needed
        }
        field_mask = "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.types"
        r = requests.post(url, json=payload, headers=self._headers(field_mask), timeout=self.timeout_s)
        r.raise_for_status()
        data = r.json()
        places = data.get("places", [])
        return places

    def place_details(self, place_id: str) -> dict:
        url = f"{PLACES_BASE}/places/{place_id}"
        field_mask = ",".join([
            "id",
            "displayName",
            "formattedAddress",
            "location",
            "rating",
            "userRatingCount",
            "types",
            "websiteUri",
            "nationalPhoneNumber",
            "priceLevel",
            "businessStatus",
            "regularOpeningHours",
            "reviews",
        ])
        r = requests.get(url, headers=self._headers(field_mask), timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()


def polite_sleep(i: int, base: float = 0.25):
    # simple throttling
    time.sleep(base + (i % 3) * base)
