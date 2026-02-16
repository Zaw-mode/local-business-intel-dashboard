"""Train a local revenue proxy model from engineered shop signals."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from acji.config import Settings


FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "price_tier",
    "rating",
    "review_count",
    "traffic_proxy",
    "source_count",
    "overall_score",
]



def _load_training_data(settings: Settings) -> pd.DataFrame:
    with duckdb.connect(str(settings.duckdb_path)) as conn:
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        if "analytics_shop_features" in tables:
            return conn.execute("SELECT * FROM analytics_shop_features").df()
        return conn.execute("SELECT * FROM shops_master").df()



def _build_revenue_target(df: pd.DataFrame) -> pd.Series:
    """Create a synthetic revenue proxy target from observable marketplace signals."""

    traffic = df["traffic_proxy"].fillna(0.5)
    rating = df["rating"].fillna(3.5)
    reviews = df["review_count"].fillna(0)
    price = df["price_tier"].fillna(2.5)

    base = 400 + (traffic * 900) + (rating * 120) + (np.log1p(reviews) * 180) + ((5 - price) * 60)
    return base



def train_revenue_model(settings: Settings) -> dict:
    """Train and persist a revenue proxy model to local disk."""

    df = _load_training_data(settings)
    if df.empty:
        raise ValueError("No data found in DuckDB. Run the ETL pipeline first.")

    for column in FEATURE_COLUMNS:
        if column not in df.columns:
            df[column] = np.nan

    feature_frame = df[FEATURE_COLUMNS].copy()
    feature_frame["price_tier"] = feature_frame["price_tier"].fillna(2.5)
    feature_frame["rating"] = feature_frame["rating"].fillna(3.5)
    feature_frame["review_count"] = feature_frame["review_count"].fillna(0)
    feature_frame["traffic_proxy"] = feature_frame["traffic_proxy"].fillna(0.4)
    feature_frame["source_count"] = feature_frame["source_count"].fillna(1)
    feature_frame["overall_score"] = feature_frame["overall_score"].fillna(50)
    feature_frame = feature_frame.fillna(feature_frame.median(numeric_only=True))

    target = _build_revenue_target(df)

    x_train, x_test, y_train, y_test = train_test_split(
        feature_frame, target, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=300, random_state=42)
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "rows": int(len(feature_frame)),
        "features": FEATURE_COLUMNS,
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }

    settings.model_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, settings.model_artifact_path)
    with settings.model_metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)

    return metrics
