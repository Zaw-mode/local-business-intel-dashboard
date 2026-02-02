# Tableau Public + “live” data (reality check)

Tableau Public **does not** behave like a live dashboard connected to your local machine.

- When you publish to Tableau Public, Tableau typically publishes an **extract**.
- If your source is a local CSV/SQLite file, Tableau Public will **not automatically refresh** when you change the file.

## How we make it feel “live” anyway

Recommended workflow:

1) Use OpenClaw cron (or manual) to regenerate `output/*.csv` on a schedule.
2) Re-publish / replace the data source on Tableau Public.

If you want fully automated refresh, we need the data hosted somewhere Tableau can reach (Tableau Cloud/Server with refresh schedules, or a public database endpoint). We can still keep costs near-zero, but it’s a different architecture.
