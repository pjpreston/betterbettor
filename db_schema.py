"""
Creates the SQLite database schema for race data.
Schema is derived from the 4 JSON files produced by racing_api.py:
  course_regions.json, courses.json, racecards.json, results.json

Database is created at /home/pete/projects/BB/DATA/racing.db.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/home/pete/projects/BB/DATA/racing.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS regions (
    region_code TEXT PRIMARY KEY,
    region      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    course_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    region_code TEXT REFERENCES regions(region_code)
);

CREATE TABLE IF NOT EXISTS horses (
    horse_id TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    region   TEXT,
    colour   TEXT,
    sex      TEXT,
    sex_code TEXT
);

CREATE TABLE IF NOT EXISTS jockeys (
    jockey_id TEXT PRIMARY KEY,
    name      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trainers (
    trainer_id TEXT PRIMARY KEY,
    name       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS owners (
    owner_id TEXT PRIMARY KEY,
    name     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS races (
    race_id         TEXT PRIMARY KEY,
    course_id       TEXT REFERENCES courses(course_id),
    date            TEXT,
    off_time        TEXT,
    off_dt          TEXT,
    race_name       TEXT,
    distance_f      TEXT,
    region          TEXT,
    pattern         TEXT,
    race_class      TEXT,
    race_type       TEXT,
    age_band        TEXT,
    rating_band     TEXT,
    sex_restriction TEXT,
    prize           TEXT,
    going           TEXT,
    surface         TEXT,
    field_size      INTEGER
);

CREATE TABLE IF NOT EXISTS race_entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    race_id         TEXT REFERENCES races(race_id),
    horse_id        TEXT REFERENCES horses(horse_id),
    jockey_id       TEXT REFERENCES jockeys(jockey_id),
    trainer_id      TEXT REFERENCES trainers(trainer_id),
    owner_id        TEXT REFERENCES owners(owner_id),
    number          TEXT,
    draw            TEXT,
    headgear        TEXT,
    age             TEXT,
    lbs             TEXT,
    ofr             TEXT,
    last_run        TEXT,
    form            TEXT,
    position        TEXT,
    weight          TEXT,
    weight_lbs      TEXT,
    official_rating TEXT
);
"""


def create_schema():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    con.commit()
    con.close()
    print(f"Database created at {DB_PATH}")


def main():
    create_schema()
    con = sqlite3.connect(DB_PATH)
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    con.close()
    print("Tables:", tables)


if __name__ == "__main__":
    main()
