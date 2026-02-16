from acji.etl.normalize import normalize_records



def test_normalize_records_handles_all_sources() -> None:
    raw_records = [
        {
            "source": "overpass",
            "fetched_at": "2026-01-01T00:00:00Z",
            "payload": {
                "type": "node",
                "id": 100,
                "lat": 30.27,
                "lon": -97.74,
                "tags": {
                    "name": "Test Cafe",
                    "amenity": "cafe",
                    "addr:city": "Austin",
                    "addr:state": "TX",
                    "price": "$$",
                },
            },
        },
        {
            "source": "foursquare",
            "fetched_at": "2026-01-01T00:00:00Z",
            "payload": {
                "fsq_id": "fsq_1",
                "name": "FSQ Coffee",
                "categories": [{"name": "Coffee Shop"}],
                "geocodes": {"main": {"latitude": 30.28, "longitude": -97.75}},
                "location": {"locality": "Austin", "region": "TX"},
                "rating": 4.4,
                "stats": {"total_ratings": 80},
            },
        },
        {
            "source": "nominatim",
            "fetched_at": "2026-01-01T00:00:00Z",
            "payload": {
                "place_id": 123,
                "name": "Nominatim Juice",
                "lat": "30.29",
                "lon": "-97.76",
                "type": "cafe",
                "address": {"city": "Austin", "state": "Texas", "postcode": "78701"},
            },
        },
    ]

    df = normalize_records(raw_records)

    assert len(df) == 3
    assert {"source", "name", "latitude", "longitude", "price_tier"}.issubset(df.columns)
    assert sorted(df["source"].unique().tolist()) == ["foursquare", "nominatim", "overpass"]
    assert df[df["source"] == "overpass"]["price_tier"].iloc[0] == 2.0
