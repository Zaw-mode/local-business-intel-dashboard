# Design notes

## Why Places API (New)
- Larger dataset and modern endpoints.
- Field masks to control cost/size.

## Storage
SQLite is used for copyability. If you need multi-user, migrate to Postgres.

## Tableau
We export CSVs because Tableau Public is easiest to share and requires no credentials for viewers.

