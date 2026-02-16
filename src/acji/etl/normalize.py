"""Normalize raw provider payloads into a unified schema."""

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd

from acji.utils.geo import normalize_name



def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None



def _to_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None



def _parse_price_tier(value: Any) -> float | None:
    """Normalize provider-specific price representations into 1..4 tiers."""

    if value is None:
        return None

    if isinstance(value, (int, float)):
        numeric = float(value)
        if 1.0 <= numeric <= 4.0:
            return numeric
        return None

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None

        # Common price notation used by provider/OSM style tags.
        dollar_count = raw.count("$")
        if dollar_count:
            return float(max(1, min(4, dollar_count)))

        match = re.search(r"(\d+(?:\.\d+)?)", raw)
        if match:
            parsed = float(match.group(1))
            if 1.0 <= parsed <= 4.0:
                return parsed

    return None



def _normalize_overpass(payload: dict[str, Any], fetched_at: str) -> dict[str, Any]:
    tags = payload.get("tags", {})
    center = payload.get("center", {})

    lat = _to_float(payload.get("lat") or center.get("lat"))
    lon = _to_float(payload.get("lon") or center.get("lon"))

    return {
        "source": "overpass",
        "source_id": f"osm_{payload.get('type', 'entity')}_{payload.get('id', '')}",
        "name": tags.get("name") or "Unknown",
        "normalized_name": normalize_name(tags.get("name") or "Unknown"),
        "category": tags.get("amenity") or tags.get("shop") or "unknown",
        "address": " ".join(
            part
            for part in [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
            ]
            if part
        ).strip()
        or None,
        "city": tags.get("addr:city") or "Austin",
        "state": tags.get("addr:state") or "TX",
        "postal_code": tags.get("addr:postcode"),
        "latitude": lat,
        "longitude": lon,
        "price_tier": _parse_price_tier(tags.get("price")),
        "rating": None,
        "review_count": None,
        "is_open_now": None,
        "url": tags.get("website"),
        "fetched_at": fetched_at,
        "raw_payload": json.dumps(payload),
    }



def _normalize_foursquare(payload: dict[str, Any], fetched_at: str) -> dict[str, Any]:
    geocodes = payload.get("geocodes", {}).get("main", {})
    location = payload.get("location", {})
    stats = payload.get("stats", {})
    categories = payload.get("categories", [])

    category = None
    if categories:
        category = categories[0].get("name")

    return {
        "source": "foursquare",
        "source_id": payload.get("fsq_id"),
        "name": payload.get("name") or "Unknown",
        "normalized_name": normalize_name(payload.get("name") or "Unknown"),
        "category": category or "unknown",
        "address": location.get("formatted_address") or location.get("address"),
        "city": location.get("locality") or "Austin",
        "state": location.get("region") or "TX",
        "postal_code": location.get("postcode"),
        "latitude": _to_float(geocodes.get("latitude")),
        "longitude": _to_float(geocodes.get("longitude")),
        "price_tier": _parse_price_tier(payload.get("price")),
        "rating": _to_float(payload.get("rating")),
        "review_count": _to_int(stats.get("total_ratings")),
        "is_open_now": payload.get("hours", {}).get("open_now"),
        "url": payload.get("website"),
        "fetched_at": fetched_at,
        "raw_payload": json.dumps(payload),
    }



def _extract_nominatim_name(payload: dict[str, Any]) -> str:
    explicit_name = payload.get("name")
    if explicit_name:
        return str(explicit_name)

    display_name = str(payload.get("display_name") or "")
    if display_name:
        return display_name.split(",")[0].strip() or "Unknown"

    return "Unknown"



def _normalize_nominatim(payload: dict[str, Any], fetched_at: str) -> dict[str, Any]:
    address = payload.get("address", {})
    name = _extract_nominatim_name(payload)

    return {
        "source": "nominatim",
        "source_id": f"nominatim_{payload.get('place_id', payload.get('osm_id', ''))}",
        "name": name,
        "normalized_name": normalize_name(name),
        "category": payload.get("type") or payload.get("class") or payload.get("_query_term") or "unknown",
        "address": " ".join(
            part
            for part in [
                address.get("house_number"),
                address.get("road"),
            ]
            if part
        ).strip()
        or None,
        "city": address.get("city")
        or address.get("town")
        or address.get("village")
        or "Austin",
        "state": address.get("state") or "TX",
        "postal_code": address.get("postcode"),
        "latitude": _to_float(payload.get("lat")),
        "longitude": _to_float(payload.get("lon")),
        "price_tier": None,
        "rating": None,
        "review_count": None,
        "is_open_now": None,
        "url": None,
        "fetched_at": fetched_at,
        "raw_payload": json.dumps(payload),
    }



def normalize_records(raw_records: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert raw extracted records to a uniform tabular DataFrame."""

    normalized_rows: list[dict[str, Any]] = []

    for record in raw_records:
        source = record.get("source")
        payload = record.get("payload", {})
        fetched_at = record.get("fetched_at")

        if source == "overpass":
            normalized_rows.append(_normalize_overpass(payload, fetched_at))
        elif source == "foursquare":
            normalized_rows.append(_normalize_foursquare(payload, fetched_at))
        elif source == "nominatim":
            normalized_rows.append(_normalize_nominatim(payload, fetched_at))

    if not normalized_rows:
        return pd.DataFrame(
            columns=[
                "source",
                "source_id",
                "name",
                "normalized_name",
                "category",
                "address",
                "city",
                "state",
                "postal_code",
                "latitude",
                "longitude",
                "price_tier",
                "rating",
                "review_count",
                "is_open_now",
                "url",
                "fetched_at",
                "raw_payload",
            ]
        )

    df = pd.DataFrame(normalized_rows)
    df = df.dropna(subset=["name", "latitude", "longitude"]).copy()
    df["review_count"] = df["review_count"].fillna(0).astype(int)
    return df
