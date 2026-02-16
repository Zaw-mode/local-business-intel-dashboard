import os
from pathlib import Path

import duckdb

from acji.config import get_settings
from acji.etl.pipeline import run_pipeline



def test_pipeline_smoke(tmp_path: Path, monkeypatch) -> None:
    duckdb_path = tmp_path / "acji_test.duckdb"
    quality_dir = tmp_path / "quality"
    model_dir = tmp_path / "models"

    monkeypatch.setenv("DUCKDB_PATH", str(duckdb_path))
    monkeypatch.setenv("GE_RESULTS_DIR", str(quality_dir))
    monkeypatch.setenv("MODEL_ARTIFACT_PATH", str(model_dir / "model.joblib"))
    monkeypatch.setenv("MODEL_METRICS_PATH", str(model_dir / "metrics.json"))
    monkeypatch.setenv("FOURSQUARE_API_KEY", "")

    get_settings.cache_clear()

    raw_records = [
        {
            "source": "overpass",
            "fetched_at": "2026-01-01T00:00:00Z",
            "payload": {
                "type": "node",
                "id": 1,
                "lat": 30.2672,
                "lon": -97.7431,
                "tags": {"name": "A Coffee", "amenity": "cafe", "addr:city": "Austin"},
            },
        },
        {
            "source": "overpass",
            "fetched_at": "2026-01-01T00:00:00Z",
            "payload": {
                "type": "node",
                "id": 2,
                "lat": 30.2772,
                "lon": -97.7531,
                "tags": {"name": "B Juice", "amenity": "juice_bar", "addr:city": "Austin"},
            },
        },
    ]

    summary = run_pipeline(run_dbt=False, raw_records_override=raw_records)

    assert summary["raw_records"] == 2
    assert summary["normalized_records"] == 2
    assert summary["deduplicated_shops"] == 2
    assert os.path.exists(summary["duckdb_path"])

    with duckdb.connect(summary["duckdb_path"]) as conn:
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}

    assert "shops_master" in tables
    assert "analytics_cheapest_shops" in tables
    assert "analytics_market_opportunity" in tables
