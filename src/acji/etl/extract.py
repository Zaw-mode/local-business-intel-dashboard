"""Extract step: fetch raw shop data from public APIs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from acji.clients import FoursquareClient, NominatimClient, OverpassClient
from acji.config import Settings



def extract_raw_records(settings: Settings) -> list[dict[str, Any]]:
    """Collect raw records from OSM Overpass, Nominatim, and Foursquare.

    API keys are read from environment-based settings and are never embedded here.
    """

    timestamp = datetime.now(timezone.utc).isoformat()
    records: list[dict[str, Any]] = []

    overpass_client = OverpassClient(endpoint=settings.overpass_endpoint)
    osm_records = overpass_client.fetch_places(
        lat=settings.austin_lat,
        lon=settings.austin_lon,
        radius_m=settings.search_radius_meters,
    )
    records.extend(
        {
            "source": "overpass",
            "fetched_at": timestamp,
            "payload": payload,
        }
        for payload in osm_records
    )

    nominatim_client = NominatimClient(
        endpoint=settings.nominatim_endpoint,
        user_agent=settings.http_user_agent,
        request_delay_seconds=settings.nominatim_request_delay_seconds,
    )
    nominatim_records = nominatim_client.fetch_places(
        lat=settings.austin_lat,
        lon=settings.austin_lon,
        radius_m=settings.search_radius_meters,
    )
    records.extend(
        {
            "source": "nominatim",
            "fetched_at": timestamp,
            "payload": payload,
        }
        for payload in nominatim_records
    )

    foursquare_client = FoursquareClient(api_key=settings.foursquare_api_key)
    fsq_records = foursquare_client.fetch_places(
        lat=settings.austin_lat,
        lon=settings.austin_lon,
        radius_m=settings.search_radius_meters,
    )
    records.extend(
        {
            "source": "foursquare",
            "fetched_at": timestamp,
            "payload": payload,
        }
        for payload in fsq_records
    )

    return records
