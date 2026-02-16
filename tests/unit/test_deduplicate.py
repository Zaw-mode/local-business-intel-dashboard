import pandas as pd

from acji.etl.deduplicate import deduplicate_records



def test_deduplicate_merges_nearby_same_name_records() -> None:
    df = pd.DataFrame(
        [
            {
                "source": "nominatim",
                "source_id": "n1",
                "name": "Sunrise Coffee",
                "normalized_name": "sunrise",
                "category": "Coffee",
                "address": "100 Main St",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "latitude": 30.2672,
                "longitude": -97.7430,
                "price_tier": 2,
                "rating": 4.3,
                "review_count": 120,
                "is_open_now": True,
                "url": "https://example.com/1",
                "fetched_at": "2026-01-01T00:00:00Z",
            },
            {
                "source": "foursquare",
                "source_id": "f1",
                "name": "Sunrise Coffee",
                "normalized_name": "sunrise",
                "category": "Coffee Shop",
                "address": "102 Main St",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "latitude": 30.2673,
                "longitude": -97.7431,
                "price_tier": 2,
                "rating": 4.5,
                "review_count": 95,
                "is_open_now": True,
                "url": "https://example.com/2",
                "fetched_at": "2026-01-01T00:00:00Z",
            },
        ]
    )

    merged = deduplicate_records(df)

    assert len(merged) == 1
    assert merged.iloc[0]["source_count"] == 2
    assert merged.iloc[0]["review_count"] == 120
