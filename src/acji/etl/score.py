"""Scoring logic for price and traffic proxy ranking."""

from __future__ import annotations

import numpy as np
import pandas as pd

from acji.constants import SCORING_WEIGHTS, TRAFFIC_COMPONENT_WEIGHTS



def score_shops(df: pd.DataFrame) -> pd.DataFrame:
    """Compute value and traffic scores, then an overall ranking score."""

    if df.empty:
        return df.copy()

    scored = df.copy()

    # Keep raw nullable columns and expose explicit imputed values for UI clarity.
    scored["price_tier_imputed"] = scored["price_tier"].fillna(2.5).clip(lower=1.0, upper=4.0)
    scored["rating_imputed"] = scored["rating"].fillna(3.5).clip(lower=0, upper=5)
    scored["review_count_imputed"] = scored["review_count"].fillna(0).astype(int)

    scored["price_tier_source"] = np.where(scored["price_tier"].isna(), "imputed", "observed")
    scored["rating_source"] = np.where(scored["rating"].isna(), "imputed", "observed")

    price = scored["price_tier_imputed"]
    scored["price_score"] = 1.0 - (price - 1.0) / 3.0

    review_norm = np.log1p(scored["review_count_imputed"]) / np.log1p(500)
    rating_norm = scored["rating_imputed"] / 5.0
    source_norm = scored["source_count"].fillna(1).clip(lower=1, upper=3) / 3.0

    scored["traffic_proxy"] = (
        TRAFFIC_COMPONENT_WEIGHTS["reviews"] * review_norm
        + TRAFFIC_COMPONENT_WEIGHTS["rating"] * rating_norm
        + TRAFFIC_COMPONENT_WEIGHTS["source_coverage"] * source_norm
    )

    scored["overall_score"] = (
        SCORING_WEIGHTS["price"] * scored["price_score"]
        + SCORING_WEIGHTS["traffic"] * scored["traffic_proxy"]
    ) * 100

    scored["overall_score"] = scored["overall_score"].round(2)
    scored["traffic_proxy"] = scored["traffic_proxy"].round(4)
    scored["price_score"] = scored["price_score"].round(4)

    return scored.sort_values(by="overall_score", ascending=False).reset_index(drop=True)
