from __future__ import annotations

import math


def competitor_score(rating: float | None, user_rating_count: int | None) -> float | None:
    """Simple score for ranking competitors.

    This is intentionally transparent:
    - favors higher rating
    - favors more ratings (confidence) via log scale

    score ~= rating * ln(1 + user_rating_count)
    """
    if rating is None or user_rating_count is None:
        return None
    try:
        return float(rating) * math.log1p(int(user_rating_count))
    except Exception:
        return None
