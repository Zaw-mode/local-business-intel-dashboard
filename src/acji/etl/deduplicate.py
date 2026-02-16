"""Deduplicate normalized listings into a single shop master table."""

from __future__ import annotations

import hashlib
import json
from collections import Counter

import pandas as pd

from acji.utils.geo import haversine_distance_m, similarity



def _is_same_shop(left: pd.Series, right: pd.Series) -> bool:
    distance = haversine_distance_m(
        float(left["latitude"]),
        float(left["longitude"]),
        float(right["latitude"]),
        float(right["longitude"]),
    )
    name_similarity = similarity(left["normalized_name"], right["normalized_name"])

    same_name = left["normalized_name"] == right["normalized_name"]
    return (same_name and distance <= 150) or (name_similarity >= 0.88 and distance <= 100)



def _pick_mode(values: list[str | None]) -> str | None:
    filtered = [item for item in values if item]
    if not filtered:
        return None
    return Counter(filtered).most_common(1)[0][0]



def _build_shop_id(name: str, lat: float, lon: float) -> str:
    identity = f"{name}|{round(lat, 4)}|{round(lon, 4)}"
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:16]
    return f"shop_{digest}"



def deduplicate_records(df: pd.DataFrame) -> pd.DataFrame:
    """Cluster duplicate listings across sources and aggregate into one row per shop."""

    if df.empty:
        return pd.DataFrame()

    working = df.sort_values(by=["review_count", "rating"], ascending=[False, False]).reset_index(
        drop=True
    )

    clusters: list[list[int]] = []

    for idx, row in working.iterrows():
        matched = False
        for cluster in clusters:
            representative = working.loc[cluster[0]]
            if _is_same_shop(representative, row):
                cluster.append(idx)
                matched = True
                break
        if not matched:
            clusters.append([idx])

    merged_rows = []
    for cluster in clusters:
        subset = working.loc[cluster].copy()
        lat = float(subset["latitude"].mean())
        lon = float(subset["longitude"].mean())

        shop_name = _pick_mode(subset["name"].tolist()) or "Unknown"

        merged_rows.append(
            {
                "shop_id": _build_shop_id(shop_name, lat, lon),
                "name": shop_name,
                "normalized_name": _pick_mode(subset["normalized_name"].tolist()) or shop_name,
                "category": _pick_mode(subset["category"].tolist()) or "unknown",
                "address": _pick_mode(subset["address"].tolist()),
                "city": _pick_mode(subset["city"].tolist()) or "Austin",
                "state": _pick_mode(subset["state"].tolist()) or "TX",
                "postal_code": _pick_mode(subset["postal_code"].tolist()),
                "latitude": lat,
                "longitude": lon,
                "price_tier": subset["price_tier"].median(),
                "rating": subset["rating"].mean(),
                "review_count": int(subset["review_count"].max()),
                "is_open_now": bool(subset["is_open_now"].fillna(False).any()),
                "source_count": int(subset["source"].nunique()),
                "sources": ",".join(sorted(subset["source"].dropna().unique().tolist())),
                "source_ids": json.dumps(
                    subset[["source", "source_id"]].to_dict(orient="records")
                ),
                "urls": json.dumps(sorted(subset["url"].dropna().unique().tolist())),
                "fetched_at": subset["fetched_at"].max(),
            }
        )

    merged_df = pd.DataFrame(merged_rows)
    merged_df = merged_df.drop_duplicates(subset=["shop_id"]).reset_index(drop=True)
    return merged_df
