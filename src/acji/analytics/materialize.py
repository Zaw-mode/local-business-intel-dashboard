"""Run SQL analytics files against DuckDB to materialize reporting tables."""

from __future__ import annotations

from pathlib import Path

import duckdb

from acji.config import Settings



def materialize_analytics_tables(settings: Settings) -> None:
    """Execute SQL files under `sql/analytics` in deterministic order."""

    sql_dir = Path(__file__).resolve().parents[3] / "sql" / "analytics"
    query_files = [
        sql_dir / "shop_features.sql",
        sql_dir / "cheapest_shops.sql",
        sql_dir / "market_opportunity.sql",
    ]

    with duckdb.connect(str(settings.duckdb_path)) as conn:
        for query_file in query_files:
            query = query_file.read_text(encoding="utf-8")
            conn.execute(query)
