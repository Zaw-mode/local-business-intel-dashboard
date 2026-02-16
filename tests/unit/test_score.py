import pandas as pd

from acji.etl.score import score_shops



def test_score_outputs_expected_columns_and_range() -> None:
    df = pd.DataFrame(
        [
            {
                "shop_id": "shop_a",
                "name": "Alpha",
                "price_tier": 1,
                "rating": 4.7,
                "review_count": 300,
                "source_count": 3,
            },
            {
                "shop_id": "shop_b",
                "name": "Beta",
                "price_tier": 4,
                "rating": 3.8,
                "review_count": 20,
                "source_count": 1,
            },
        ]
    )

    scored = score_shops(df)

    assert {"price_score", "traffic_proxy", "overall_score"}.issubset(scored.columns)
    assert scored["overall_score"].between(0, 100).all()
    assert scored.iloc[0]["name"] == "Alpha"
