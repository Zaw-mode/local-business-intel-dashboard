#!/usr/bin/env python3
"""Run the ACJI ETL pipeline from the command line."""

from __future__ import annotations

import argparse
import json

from acji.etl.pipeline import run_pipeline



def main() -> None:
    parser = argparse.ArgumentParser(description="Run ACJI ETL pipeline")
    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Skip dbt run/test after loading data",
    )
    args = parser.parse_args()

    summary = run_pipeline(run_dbt=not args.skip_dbt)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
