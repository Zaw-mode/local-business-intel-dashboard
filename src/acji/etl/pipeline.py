"""Main ETL pipeline orchestration for ACJI."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from acji.analytics.materialize import materialize_analytics_tables
from acji.config import get_settings
from acji.etl.deduplicate import deduplicate_records
from acji.etl.extract import extract_raw_records
from acji.etl.load import load_to_duckdb
from acji.etl.normalize import normalize_records
from acji.etl.score import score_shops
from acji.quality.expectations import run_quality_checks



def _run_dbt(project_dir: Path, profiles_dir: Path, target: str) -> None:
    subprocess.run(
        [
            "dbt",
            "run",
            "--project-dir",
            str(project_dir),
            "--profiles-dir",
            str(profiles_dir),
            "--target",
            target,
        ],
        check=True,
    )
    subprocess.run(
        [
            "dbt",
            "test",
            "--project-dir",
            str(project_dir),
            "--profiles-dir",
            str(profiles_dir),
            "--target",
            target,
        ],
        check=True,
    )



def run_pipeline(
    run_dbt: bool = True,
    raw_records_override: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run extraction, normalization, deduplication, scoring, quality, and analytics."""

    settings = get_settings()

    raw_records = raw_records_override if raw_records_override is not None else extract_raw_records(settings)

    normalized_df = normalize_records(raw_records)
    quality_result = run_quality_checks(normalized_df, settings.ge_results_dir)

    deduplicated_df = deduplicate_records(normalized_df)
    scored_df = score_shops(deduplicated_df)

    load_to_duckdb(raw_records, normalized_df, scored_df, settings)
    materialize_analytics_tables(settings)

    if run_dbt:
        _run_dbt(settings.dbt_project_dir, settings.dbt_profiles_dir, settings.dbt_target)

    output_csv = Path("data/processed/shops_master.csv")
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if not scored_df.empty:
        scored_df.to_csv(output_csv, index=False)

    return {
        "raw_records": len(raw_records),
        "normalized_records": int(len(normalized_df)),
        "deduplicated_shops": int(len(scored_df)),
        "quality_success": bool(quality_result["success"]),
        "output_csv": str(output_csv),
        "duckdb_path": str(settings.duckdb_path),
    }
