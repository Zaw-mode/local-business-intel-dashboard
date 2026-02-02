# Local Business Intelligence Dashboard (Places + Reviews + “Best Competitors”)

Type a **business category + area** → get a ranked list of places, review themes, and Tableau-ready exports.

## What this project does

- Pulls businesses from **Google Places API (New)**
- Pulls **place details + reviews**
- Runs lightweight text analytics to extract themes (e.g., *parking*, *service*, *price*, *wait time*)
- Stores everything in **SQLite**
- Exports clean CSVs for **Tableau Public**

## Prerequisites

- Python 3.11+
- A Google Cloud project with **Places API (New)** enabled
- A **Google Places API key** restricted to your IP (recommended)

## Security (read this)

- Do **NOT** commit API keys to git.
- Use environment variables.
- If you pasted a key in chat/logs, **rotate it** in Google Cloud.

## Configure

Set your API key as an environment variable:

**PowerShell (User env):**
```powershell
setx OPENCLAW_GOOGLE_PLACES_API_KEY "YOUR_KEY_HERE"
```
Close and reopen PowerShell.

Optional Brave Search key (for enrichment):
```powershell
setx BRAVE_API_KEY "YOUR_BRAVE_KEY_HERE"
```

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (example)

Austin coffee shops, 10 mile radius around downtown:

```bash
python -m src.run \
  --keyword "coffee shop" \
  --lat 30.2672 --lng -97.7431 \
  --radius-m 16093 \
  --limit 30
```

This writes:
- `data/bi.sqlite`
- `output/places.csv`
- `output/competitors.csv` (ranked)
- `output/reviews.csv`
- `output/themes.csv`

## Tableau Public

See `docs/tableau.md`.

In short:
1) Connect → Text/CSV → `output/competitors.csv`
2) Relate/join `themes.csv` by `place_id`
3) Build map + leaderboard + themes views
4) Publish to Tableau Public.

## Notes / limitations

- Places reviews returned by the API are limited (not all reviews).
- Quotas apply; the ETL includes throttling.

## Repo layout

- `src/` main pipeline
- `data/` SQLite DB
- `output/` CSV exports
- `docs/` design notes

