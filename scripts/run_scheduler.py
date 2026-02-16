#!/usr/bin/env python3
"""Schedule recurring ACJI ETL + model training jobs."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from acji.config import get_settings
from acji.etl.pipeline import run_pipeline
from acji.model.train import train_revenue_model


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)



def scheduled_job(skip_dbt: bool) -> None:
    logging.info("Starting scheduled pipeline run")
    summary = run_pipeline(run_dbt=not skip_dbt)
    logging.info("Pipeline summary: %s", summary)

    settings = get_settings()
    metrics = train_revenue_model(settings)
    logging.info("Model metrics: %s", metrics)



def main() -> None:
    parser = argparse.ArgumentParser(description="Run ACJI scheduler")
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=24,
        help="How often to run ETL and model training",
    )
    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Skip dbt run/test in scheduled jobs",
    )
    args = parser.parse_args()

    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_job,
        trigger="interval",
        hours=args.interval_hours,
        kwargs={"skip_dbt": args.skip_dbt},
        next_run_time=datetime.now(),
    )

    logging.info("Scheduler started; interval_hours=%s", args.interval_hours)
    scheduler.start()


if __name__ == "__main__":
    main()
