from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  keyword TEXT NOT NULL,
  lat REAL NOT NULL,
  lng REAL NOT NULL,
  radius_m INTEGER NOT NULL,
  limit_n INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS places (
  place_id TEXT PRIMARY KEY,
  name TEXT,
  address TEXT,
  lat REAL,
  lng REAL,
  rating REAL,
  user_rating_count INTEGER,
  types TEXT,
  website TEXT,
  phone TEXT,
  price_level TEXT,
  business_status TEXT,
  raw_json TEXT
);

CREATE TABLE IF NOT EXISTS reviews (
  review_id TEXT PRIMARY KEY,
  place_id TEXT NOT NULL,
  rating INTEGER,
  relative_publish_time TEXT,
  publish_time TEXT,
  text TEXT,
  language_code TEXT,
  author_name TEXT,
  raw_json TEXT,
  FOREIGN KEY(place_id) REFERENCES places(place_id)
);

CREATE TABLE IF NOT EXISTS themes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  place_id TEXT NOT NULL,
  theme TEXT NOT NULL,
  count INTEGER NOT NULL,
  sentiment REAL,
  sample TEXT,
  FOREIGN KEY(place_id) REFERENCES places(place_id)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode=WAL;")
    con.executescript(SCHEMA)
    return con
