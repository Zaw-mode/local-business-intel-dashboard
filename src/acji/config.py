"""Configuration and secure token loading.

This module reads environment variables from the runtime environment (and optional
`.env` file) so API keys are never hardcoded in source code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env if present. Real secrets stay local and out of git.
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Runtime settings for API access, storage, and orchestration."""

    acji_env: str
    austin_lat: float
    austin_lon: float
    search_radius_meters: int

    overpass_endpoint: str
    nominatim_endpoint: str
    http_user_agent: str
    nominatim_request_delay_seconds: float
    foursquare_api_key: str

    duckdb_path: Path
    ge_results_dir: Path
    model_artifact_path: Path
    model_metrics_path: Path

    dbt_project_dir: Path
    dbt_profiles_dir: Path
    dbt_target: str



def _resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables.

    Sensitive values like `FOURSQUARE_API_KEY` must come from environment
    variables. If keys are absent, the corresponding source is skipped.
    """

    duckdb_path = _resolve_path(os.getenv("DUCKDB_PATH", "./data/warehouse/acji.duckdb"))
    ge_results_dir = _resolve_path(os.getenv("GE_RESULTS_DIR", "./data/quality"))
    model_artifact_path = _resolve_path(
        os.getenv("MODEL_ARTIFACT_PATH", "./models/revenue_model.joblib")
    )
    model_metrics_path = _resolve_path(
        os.getenv("MODEL_METRICS_PATH", "./models/revenue_metrics.json")
    )
    dbt_project_dir = _resolve_path(os.getenv("DBT_PROJECT_DIR", "./dbt"))
    dbt_profiles_dir = _resolve_path(os.getenv("DBT_PROFILES_DIR", "./dbt"))

    return Settings(
        acji_env=os.getenv("ACJI_ENV", "dev"),
        austin_lat=float(os.getenv("AUSTIN_LAT", "30.2672")),
        austin_lon=float(os.getenv("AUSTIN_LON", "-97.7431")),
        search_radius_meters=int(os.getenv("SEARCH_RADIUS_METERS", "20000")),
        overpass_endpoint=os.getenv(
            "OVERPASS_ENDPOINT", "https://overpass-api.de/api/interpreter"
        ),
        nominatim_endpoint=os.getenv(
            "NOMINATIM_ENDPOINT", "https://nominatim.openstreetmap.org/search"
        ),
        http_user_agent=os.getenv(
            "ACJI_HTTP_USER_AGENT",
            "ACJI/0.1 (local development)",
        ),
        nominatim_request_delay_seconds=float(
            os.getenv("NOMINATIM_REQUEST_DELAY_SECONDS", "1.0")
        ),
        foursquare_api_key=os.getenv("FOURSQUARE_API_KEY", "").strip(),
        duckdb_path=duckdb_path,
        ge_results_dir=ge_results_dir,
        model_artifact_path=model_artifact_path,
        model_metrics_path=model_metrics_path,
        dbt_project_dir=dbt_project_dir,
        dbt_profiles_dir=dbt_profiles_dir,
        dbt_target=os.getenv("DBT_TARGET", "dev"),
    )
