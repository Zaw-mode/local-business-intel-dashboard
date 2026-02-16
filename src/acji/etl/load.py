"""Load normalized and scored data into DuckDB tables."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from acji.config import Settings



def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)



def _align_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    aligned = df.copy()
    for column in columns:
        if column not in aligned.columns:
            aligned[column] = None
    return aligned[columns]



def load_to_duckdb(
    raw_records: list[dict], normalized_df: pd.DataFrame, scored_df: pd.DataFrame, settings: Settings
) -> None:
    """Persist ETL outputs to DuckDB tables for downstream analytics and dashboarding."""

    _ensure_parent_dir(settings.duckdb_path)

    raw_columns = ["source", "fetched_at", "payload"]
    normalized_columns = [
        "source",
        "source_id",
        "name",
        "normalized_name",
        "category",
        "address",
        "city",
        "state",
        "postal_code",
        "latitude",
        "longitude",
        "price_tier",
        "rating",
        "review_count",
        "is_open_now",
        "url",
        "fetched_at",
        "raw_payload",
    ]
    master_columns = [
        "shop_id",
        "name",
        "normalized_name",
        "category",
        "address",
        "city",
        "state",
        "postal_code",
        "latitude",
        "longitude",
        "price_tier",
        "rating",
        "review_count",
        "is_open_now",
        "source_count",
        "sources",
        "source_ids",
        "urls",
        "fetched_at",
        "price_tier_imputed",
        "rating_imputed",
        "review_count_imputed",
        "price_tier_source",
        "rating_source",
        "price_score",
        "traffic_proxy",
        "overall_score",
    ]

    raw_df = pd.DataFrame(raw_records)
    if not raw_df.empty:
        raw_df["payload"] = raw_df["payload"].apply(json.dumps)
        raw_df = _align_columns(raw_df, raw_columns)

    with duckdb.connect(str(settings.duckdb_path)) as conn:
        conn.execute("DROP TABLE IF EXISTS raw_shop_listings")
        conn.execute(
            """
            CREATE TABLE raw_shop_listings (
                source VARCHAR,
                fetched_at VARCHAR,
                payload JSON
            )
            """
        )
        if not raw_df.empty:
            conn.register("raw_df", raw_df)
            conn.execute(
                "INSERT INTO raw_shop_listings SELECT source, fetched_at, payload::JSON FROM raw_df"
            )

        conn.execute("DROP TABLE IF EXISTS normalized_shop_listings")
        conn.execute(
            """
            CREATE TABLE normalized_shop_listings (
                source VARCHAR,
                source_id VARCHAR,
                name VARCHAR,
                normalized_name VARCHAR,
                category VARCHAR,
                address VARCHAR,
                city VARCHAR,
                state VARCHAR,
                postal_code VARCHAR,
                latitude DOUBLE,
                longitude DOUBLE,
                price_tier DOUBLE,
                rating DOUBLE,
                review_count INTEGER,
                is_open_now BOOLEAN,
                url VARCHAR,
                fetched_at VARCHAR,
                raw_payload VARCHAR
            )
            """
        )
        if not normalized_df.empty:
            normalized_aligned = _align_columns(normalized_df, normalized_columns)
            conn.register("normalized_df", normalized_aligned)
            conn.execute("INSERT INTO normalized_shop_listings SELECT * FROM normalized_df")

        conn.execute("DROP TABLE IF EXISTS shops_master")
        conn.execute(
            """
            CREATE TABLE shops_master (
                shop_id VARCHAR,
                name VARCHAR,
                normalized_name VARCHAR,
                category VARCHAR,
                address VARCHAR,
                city VARCHAR,
                state VARCHAR,
                postal_code VARCHAR,
                latitude DOUBLE,
                longitude DOUBLE,
                price_tier DOUBLE,
                rating DOUBLE,
                review_count INTEGER,
                is_open_now BOOLEAN,
                source_count INTEGER,
                sources VARCHAR,
                source_ids VARCHAR,
                urls VARCHAR,
                fetched_at VARCHAR,
                price_tier_imputed DOUBLE,
                rating_imputed DOUBLE,
                review_count_imputed INTEGER,
                price_tier_source VARCHAR,
                rating_source VARCHAR,
                price_score DOUBLE,
                traffic_proxy DOUBLE,
                overall_score DOUBLE
            )
            """
        )
        if not scored_df.empty:
            master_aligned = _align_columns(scored_df, master_columns)
            conn.register("scored_df", master_aligned)
            conn.execute("INSERT INTO shops_master SELECT * FROM scored_df")
