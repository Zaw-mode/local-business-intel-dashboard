"""Great Expectations checks for normalized ETL outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import great_expectations as ge
import pandas as pd



def run_quality_checks(df: pd.DataFrame, output_dir: Path) -> dict[str, Any]:
    """Run Great Expectations checks and persist result JSON locally."""

    output_dir.mkdir(parents=True, exist_ok=True)

    if df.empty:
        result = {
            "success": False,
            "reason": "No records were available for validation.",
            "expectations": [],
        }
    else:
        ge_df = ge.from_pandas(df)
        checks = [
            ge_df.expect_column_values_to_not_be_null("name"),
            ge_df.expect_column_values_to_not_be_null("latitude"),
            ge_df.expect_column_values_to_not_be_null("longitude"),
            ge_df.expect_column_values_to_be_between("latitude", min_value=-90, max_value=90),
            ge_df.expect_column_values_to_be_between("longitude", min_value=-180, max_value=180),
            ge_df.expect_column_values_to_be_between(
                "price_tier", min_value=1, max_value=4, mostly=0.70, allow_cross_type_comparisons=True
            ),
            ge_df.expect_column_values_to_be_between(
                "review_count", min_value=0, mostly=1.0, allow_cross_type_comparisons=True
            ),
        ]
        result = {
            "success": all(check.success for check in checks),
            "reason": "",
            "expectations": [check.to_json_dict() for check in checks],
        }

    result_file = output_dir / "great_expectations_validation.json"
    with result_file.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    return result
