# Austin Coffee & Juice Intelligence (ACJI)

ACJI is a secure, local-first ETL + analytics project that collects Austin coffee/juice listings from public APIs, standardizes and deduplicates them, scores each location for value and traffic proxy, produces analytics tables, trains a revenue proxy model, and serves an interactive Streamlit dashboard.

## Security First: API Keys and Tokens

ACJI **never hardcodes secrets** in source code.

- API keys are loaded only from environment variables.
- `.env` is ignored by git.
- `.env.example` is committed as a safe template with placeholders.
- No auth tokens are stored in Python files, JSON config files, or dbt project code.

### Required environment variables

- None for free-only mode (Overpass + Nominatim).

### Optional environment variables

- `FOURSQUARE_API_KEY` (enables richer ratings/price coverage)
- `OVERPASS_ENDPOINT` (defaults to public Overpass endpoint)
- `NOMINATIM_ENDPOINT` (defaults to public Nominatim endpoint)
- `ACJI_HTTP_USER_AGENT` (set to your contact email for Nominatim policy compliance)
- `NOMINATIM_REQUEST_DELAY_SECONDS` (defaults to `1.0`)
- `DUCKDB_PATH`
- `GE_RESULTS_DIR`
- `MODEL_ARTIFACT_PATH`
- `MODEL_METRICS_PATH`
- `DBT_PROJECT_DIR`
- `DBT_PROFILES_DIR`
- `DBT_TARGET`

## Project Tree

```text
.
├── .env.example
├── .gitignore
├── Dockerfile
├── Makefile
├── README.md
├── dashboard/
│   └── app.py
├── data/
│   ├── processed/.gitkeep
│   ├── quality/.gitkeep
│   ├── raw/.gitkeep
│   └── warehouse/.gitkeep
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── profiles.yml.example
│   └── models/
│       ├── marts/
│       │   ├── cheapest_shops.sql
│       │   ├── market_opportunity.sql
│       │   ├── schema.yml
│       │   └── shop_features.sql
│       ├── sources.yml
│       └── staging/stg_shops.sql
├── docker-compose.yml
├── logs/.gitkeep
├── models/.gitkeep
├── pyproject.toml
├── requirements.txt
├── scripts/
│   ├── run_dashboard.sh
│   ├── run_pipeline.py
│   ├── run_scheduler.py
│   └── train_model.py
├── sql/
│   └── analytics/
│       ├── cheapest_shops.sql
│       ├── market_opportunity.sql
│       └── shop_features.sql
├── src/
│   └── acji/
│       ├── __init__.py
│       ├── analytics/materialize.py
│       ├── clients/
│       │   ├── foursquare.py
│       │   ├── nominatim.py
│       │   ├── overpass.py
│       │   └── paid_source_compat.py
│       ├── config.py
│       ├── constants.py
│       ├── etl/
│       │   ├── deduplicate.py
│       │   ├── extract.py
│       │   ├── load.py
│       │   ├── normalize.py
│       │   ├── pipeline.py
│       │   └── score.py
│       ├── model/train.py
│       ├── quality/expectations.py
│       └── utils/geo.py
└── tests/
    ├── integration/test_pipeline_smoke.py
    └── unit/
        ├── test_deduplicate.py
        ├── test_normalize.py
        └── test_score.py
```

## Data Sources

1. OpenStreetMap Overpass API (free)
1. OpenStreetMap Nominatim Search API (free)
1. Foursquare Places API (optional key)

## ETL + Analytics Workflow

1. Extract raw records from APIs.
1. Normalize records into a unified schema.
1. Deduplicate cross-source records into `shops_master`.
1. Score each shop:
- `price_score` for affordability
- `traffic_proxy` for demand signal
- `overall_score` weighted rank
- `price_tier_imputed` / `rating_imputed` so UI does not show unexplained nulls
1. Validate data quality with Great Expectations.
1. Load curated data to DuckDB.
1. Materialize analytics tables via SQL and dbt:
- `analytics_cheapest_shops`
- `analytics_market_opportunity`
- `analytics_shop_features`
1. Train a local revenue proxy model using scikit-learn.
1. Serve dashboard for ranking and simulation.

## macOS Setup

### 1. Install prerequisites

```bash
brew install python@3.11
python3 --version
```

### 2. Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### 3. Configure environment variables securely

```bash
cp .env.example .env
```

Edit `.env` with your values. For free-only mode, leave `FOURSQUARE_API_KEY` blank.

```dotenv
FOURSQUARE_API_KEY=
ACJI_HTTP_USER_AGENT=ACJI/0.1 (your-email@example.com)
```

Optional: load env vars into current shell

```bash
set -a
source .env
set +a
```

## Run the Pipeline

### Full pipeline with dbt

```bash
python scripts/run_pipeline.py
```

### Pipeline without dbt

```bash
python scripts/run_pipeline.py --skip-dbt
```

## Run dbt directly

```bash
dbt run --project-dir dbt --profiles-dir dbt
dbt test --project-dir dbt --profiles-dir dbt
```

## Train Revenue Proxy Model

```bash
python scripts/train_model.py
```

Outputs:
- model artifact at `MODEL_ARTIFACT_PATH` (default: `models/revenue_model.joblib`)
- metrics JSON at `MODEL_METRICS_PATH` (default: `models/revenue_metrics.json`)

## Launch Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

Dashboard includes:
- Austin shop map with interactive filters
- ranked shop table
- scoring explanation
- observed vs imputed value visibility for price/rating
- market opportunity table
- location simulator with revenue proxy prediction

## Scheduler (Airflow alternative)

Run recurring jobs every 24 hours (default):

```bash
python scripts/run_scheduler.py
```

Custom interval in hours:

```bash
python scripts/run_scheduler.py --interval-hours 12
```

## Testing

```bash
pytest
```

Test coverage includes:
- normalization logic
- deduplication logic
- scoring logic
- integration smoke test for end-to-end pipeline load

## DuckDB Tables

Core tables:
- `raw_shop_listings`
- `normalized_shop_listings`
- `shops_master`

Analytics tables:
- `analytics_shop_features`
- `analytics_cheapest_shops`
- `analytics_market_opportunity`

## Secure Token Management Notes

- Keep `.env` local and private.
- Never paste keys into notebooks, scripts, or source-controlled config files.
- Rotate API keys if accidentally exposed.
- CI/CD (if added) should provide secrets via environment variables or secret manager.

## Optional Docker Usage

Build and run dashboard container:

```bash
docker compose up --build
```

Container reads variables from local `.env`.

## Common Issues

- `No paid API key`: free mode still works with Overpass + Nominatim.
- `Nominatim 403/429`: set a valid `ACJI_HTTP_USER_AGENT` and keep request delay at `>=1.0`.
- `No data in dashboard`: run `python scripts/run_pipeline.py` first.
