"""
Creates the SQLite database schema for the BB database (KAN-27).

A single denormalized RACING table whose columns mirror the Racing Post
CSV at /home/pete/projects/BB/DATA/RP/DATA/region/all/all/<YYYY_MM_DD>.csv.

The CSV column "or" (Official Rating) is renamed to "official_rating"
in the table to avoid colliding with the SQL reserved word.

Database is created at /home/pete/projects/BB/DATABASE/BB.db.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("/home/pete/projects/BB/DATABASE/BB.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS RACING (
    date             TEXT NOT NULL,
    region           TEXT,
    course           TEXT NOT NULL,
    course_detail    TEXT,
    off              TEXT NOT NULL,
    race_name        TEXT,
    type             TEXT,
    class            TEXT,
    pattern          TEXT,
    rating_band      TEXT,
    age_band         TEXT,
    sex_rest         TEXT,
    dist             TEXT,
    dist_f           REAL,
    dist_m           INTEGER,
    going            TEXT,
    surface          TEXT,
    ran              INTEGER,
    num              INTEGER,
    pos              TEXT,
    draw             INTEGER,
    ovr_btn          TEXT,
    btn              TEXT,
    horse            TEXT NOT NULL,
    age              INTEGER,
    sex              TEXT,
    lbs              INTEGER,
    hg               TEXT,
    time             TEXT,
    secs             REAL,
    dec              REAL,
    jockey           TEXT,
    trainer          TEXT,
    prize            REAL,
    official_rating  INTEGER,
    rpr              TEXT,
    sire             TEXT,
    dam              TEXT,
    damsire          TEXT,
    owner            TEXT,
    comment          TEXT,
    PRIMARY KEY (date, course, off, horse)
);
"""


def create_schema(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    try:
        con.executescript(SCHEMA)
        con.commit()
    finally:
        con.close()


def main() -> None:
    create_schema()
    con = sqlite3.connect(DB_PATH)
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    con.close()
    print(f"Database created at {DB_PATH}")
    print("Tables:", tables)


if __name__ == "__main__":
    main()
