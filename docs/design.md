# Design notes

## Why Places API (New)
- Larger dataset and modern endpoints.
- Field masks to control cost/size.

## Area → lat/lng (no key)
We geocode `--area` (e.g. "Austin, TX") using OpenStreetMap Nominatim to avoid needing Google Geocoding.

## Storage
SQLite is used for copyability. If you need multi-user, migrate to Postgres.

## Tableau
We export CSVs because Tableau Public is easiest to share and requires no credentials for viewers.

