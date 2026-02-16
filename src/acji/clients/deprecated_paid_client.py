"""Deprecated paid-source compatibility placeholder.

ACJI uses free providers (Overpass + Nominatim) for default runtime behavior.
This module remains only as a compatibility stub for older imports.
"""

from __future__ import annotations

from typing import Any


class DeprecatedPaidClient:
    """Deprecated compatibility stub.

    Do not use for new pipelines.
    """

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def fetch_places(self, *_args: Any, **_kwargs: Any) -> list[dict[str, Any]]:
        raise RuntimeError(
            "Deprecated paid-source integration is disabled. Use Overpass + Nominatim + optional Foursquare."
        )
