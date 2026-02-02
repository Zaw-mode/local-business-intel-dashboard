# Tableau Public guide

## Quick setup

1. Tableau → **Connect** → **Text/CSV** → pick:
   - `output/competitors.csv`
2. Add map:
   - Drag `lat` and `lng` to the view (or use generated Latitude/Longitude)
   - Put `name` on Label
   - Put `score` on Size or Color
3. Add themes:
   - Connect another CSV: `output/themes.csv`
   - Relate/Join on `place_id`

## Suggested sheets

- **Map**: competitor pins sized by score
- **Leaderboard**: top N by score, include rating + count
- **Themes**:
  - Top themes overall (sum count)
  - Theme vs score scatter

