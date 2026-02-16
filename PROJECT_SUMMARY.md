# ACJI Project Summary

## What It Does
Austin Coffee & Juice Intelligence (ACJI) is an end-to-end ETL and analytics system that discovers Austin coffee/juice businesses, normalizes and deduplicates them, computes affordability and traffic-proxy scores, and serves insights in an interactive dashboard.

## Data Sources
- OpenStreetMap Overpass API (free)
- OpenStreetMap Nominatim API (free)
- Foursquare Places API (optional enrichment)

## Pipeline Flow
1. Extract from APIs.
2. Normalize to a shared schema.
3. Deduplicate across providers into `shops_master`.
4. Score shops (`price_score`, `traffic_proxy`, `overall_score`).
5. Validate with Great Expectations.
6. Load into DuckDB.
7. Materialize analytics tables (SQL + dbt).
8. Train revenue proxy model (scikit-learn).
9. Explore rankings and simulation in Streamlit.

## Key Outputs
- Core DuckDB tables:
  - `raw_shop_listings`
  - `normalized_shop_listings`
  - `shops_master`
- Analytics tables:
  - `analytics_cheapest_shops`
  - `analytics_market_opportunity`
  - `analytics_shop_features`
- Model artifacts:
  - `models/revenue_model.joblib`
  - `models/revenue_metrics.json`

## Security and Secrets
- No hardcoded tokens.
- Keys loaded from environment variables.
- `.env` excluded from git.
- `.env.example` provides safe placeholders.

## Run Commands
- Pipeline: `python scripts/run_pipeline.py`
- Model training: `python scripts/train_model.py`
- Dashboard: `streamlit run dashboard/app.py`
- Tests: `pytest`
