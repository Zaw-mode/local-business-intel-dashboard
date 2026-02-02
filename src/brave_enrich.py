from __future__ import annotations

import os
from typing import Any

import requests


def brave_search(query: str, *, count: int = 3, timeout_s: int = 20) -> list[dict[str, Any]]:
    """Optional enrichment using Brave Search API.

    Requires BRAVE_API_KEY in env.
    """
    key = os.environ.get("BRAVE_API_KEY") or os.environ.get("BRAVE_SEARCH_API_KEY")
    if not key:
        return []

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": key,
    }
    params = {"q": query, "count": max(1, min(int(count), 5))}

    r = requests.get(url, headers=headers, params=params, timeout=timeout_s)
    r.raise_for_status()
    data = r.json() or {}

    out: list[dict[str, Any]] = []
    for item in (((data.get("web") or {}).get("results")) or [])[:count]:
        out.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "description": item.get("description"),
            }
        )
    return out
