"""Project-level constants used across ETL, analytics, and dashboard modules."""

TARGET_CATEGORIES = ["coffee", "juice", "smoothie", "cafe"]

PRICE_MIN = 1.0
PRICE_MAX = 4.0

# Scoring weights are intentionally explicit for reproducibility.
SCORING_WEIGHTS = {
    "price": 0.55,
    "traffic": 0.45,
}

TRAFFIC_COMPONENT_WEIGHTS = {
    "reviews": 0.45,
    "rating": 0.35,
    "source_coverage": 0.20,
}
