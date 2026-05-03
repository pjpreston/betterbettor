"""
Loader for the BB SQLite database (KAN-27).

Reads a Racing Post CSV (one file per day, filename encodes the date,
e.g. 2026_04_28.csv) and bulk-inserts its rows into the RACING table
of /home/pete/projects/BB/DATABASE/BB.db.

The CSV column "or" is mapped to the table column "official_rating".
Inserts use INSERT OR REPLACE on the composite primary key
(date, course, off, horse) so reloading the same file is idempotent.
"""

import csv
import re
import sqlite3
import sys
from pathlib import Path

from bb_schema import DB_PATH, create_schema

CSV_COLUMNS = [
    "date", "region", "course", "course_detail", "off", "race_name", "type", "class",
    "pattern", "rating_band", "age_band", "sex_rest", "dist", "dist_f", "dist_m", "going",
    "surface", "ran", "num", "pos", "draw", "ovr_btn", "btn", "horse", "age", "sex", "lbs",
    "hg", "time", "secs", "dec", "jockey", "trainer", "prize", "or", "rpr", "sire", "dam",
    "damsire", "owner", "comment",
]

CSV_TO_DB_COLUMN = {"or": "official_rating"}

INT_COLUMNS = {"dist_m", "ran", "num", "draw", "age", "lbs", "or"}
FLOAT_COLUMNS = {"dist_f", "secs", "dec", "prize"}

_FILENAME_DATE_RE = re.compile(r"^(\d{4})_(\d{2})_(\d{2})\.csv$")


def _date_from_filename(csv_path: Path) -> str:
    m = _FILENAME_DATE_RE.match(csv_path.name)
    if not m:
        raise ValueError(f"Filename {csv_path.name!r} does not match YYYY_MM_DD.csv")
    y, mo, d = m.groups()
    return f"{y}-{mo}-{d}"


def _coerce(col: str, value):
    if value is None or value == "":
        return None
    if col == "dist_f" and isinstance(value, str) and value.endswith("f"):
        value = value[:-1]
    if col in INT_COLUMNS:
        try:
            return int(value)
        except ValueError:
            return None
    if col in FLOAT_COLUMNS:
        try:
            return float(value)
        except ValueError:
            return None
    return value


def load_csv(csv_path: Path, db_path: Path = DB_PATH) -> int:
    """Load a Racing Post CSV into the RACING table. Returns rows inserted."""
    csv_path = Path(csv_path)
    expected_date = _date_from_filename(csv_path)

    create_schema(db_path)

    db_columns = [CSV_TO_DB_COLUMN.get(c, c) for c in CSV_COLUMNS]
    columns_sql = ", ".join(db_columns)
    placeholders = ", ".join(["?"] * len(db_columns))
    sql = f"INSERT OR REPLACE INTO RACING ({columns_sql}) VALUES ({placeholders})"

    rows = []
    mismatched_dates = 0
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != CSV_COLUMNS:
            raise ValueError(
                "CSV header mismatch.\n"
                f"  expected: {CSV_COLUMNS}\n"
                f"  found:    {reader.fieldnames}"
            )
        for row in reader:
            if row["date"] != expected_date:
                mismatched_dates += 1
            rows.append(tuple(_coerce(col, row[col]) for col in CSV_COLUMNS))

    if mismatched_dates:
        print(
            f"warning: {mismatched_dates} row(s) in {csv_path.name} have a date "
            f"that does not match the filename date ({expected_date})",
            file=sys.stderr,
        )

    con = sqlite3.connect(db_path)
    try:
        with con:
            con.executemany(sql, rows)
    finally:
        con.close()

    return len(rows)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <path-to-csv>", file=sys.stderr)
        return 2
    n = load_csv(Path(argv[1]))
    print(f"Loaded {n} rows into RACING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
