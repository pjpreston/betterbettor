"""Tests for bb_schema.py and bb_loader.py (KAN-27).

Schema/idempotency checks run against a temp-dir DB. The full-CSV load test
requires the real input file at
/home/pete/projects/BB/DATA/RP/DATA/region/all/all/2026_04_28.csv;
it is skipped if that file is missing.
"""

import sqlite3
import tempfile
import unittest
from pathlib import Path

import bb_schema
import bb_loader

CSV_PATH = Path("/home/pete/projects/BB/DATA/RP/DATA/region/all/all/2026_04_28.csv")
BETFAIR_CSV_PATH = Path("/home/pete/projects/BB/DATA/RP/DATA/region/all/all/2026_03_05.csv")
EXPECTED_COLUMNS = [
    "date", "region", "course", "course_detail", "off", "race_name", "type", "class",
    "pattern", "rating_band", "age_band", "sex_rest", "dist", "dist_f", "dist_m", "going",
    "surface", "ran", "num", "pos", "draw", "ovr_btn", "btn", "horse", "age", "sex", "lbs",
    "hg", "time", "secs", "dec", "jockey", "trainer", "prize", "official_rating", "rpr",
    "sire", "dam", "damsire", "owner", "comment",
    "bsp", "pre_min", "pre_max", "ip_min", "ip_max", "pre_vol", "ip_vol",
]


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "BB.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_create_schema_creates_racing_table_with_expected_columns(self):
        bb_schema.create_schema(self.db_path)
        con = sqlite3.connect(self.db_path)
        try:
            tables = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )]
            self.assertEqual(tables, ["RACING"])

            cols = [r[1] for r in con.execute("PRAGMA table_info(RACING)")]
            self.assertEqual(cols, EXPECTED_COLUMNS)
            self.assertIn("official_rating", cols)
            self.assertNotIn("or", cols)

            pk_cols = [r[1] for r in con.execute("PRAGMA table_info(RACING)") if r[5] > 0]
            self.assertEqual(set(pk_cols), {"date", "course", "off", "horse"})
        finally:
            con.close()

    def test_create_schema_is_idempotent(self):
        bb_schema.create_schema(self.db_path)
        bb_schema.create_schema(self.db_path)  # second call must not fail


class FilenameDateTests(unittest.TestCase):
    def test_well_formed_filename(self):
        self.assertEqual(
            bb_loader._date_from_filename(Path("2026_04_28.csv")),
            "2026-04-28",
        )

    def test_well_formed_filename_with_directory(self):
        self.assertEqual(
            bb_loader._date_from_filename(Path("/some/dir/2025_12_01.csv")),
            "2025-12-01",
        )

    def test_bad_filename_raises(self):
        with self.assertRaises(ValueError):
            bb_loader._date_from_filename(Path("not_a_date.csv"))
        with self.assertRaises(ValueError):
            bb_loader._date_from_filename(Path("2026-04-28.csv"))


@unittest.skipUnless(CSV_PATH.exists(), f"Input CSV not present at {CSV_PATH}")
class LoadCsvTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "BB.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_inserts_all_rows(self):
        n = bb_loader.load_csv(CSV_PATH, db_path=self.db_path)
        self.assertEqual(n, 420)

        con = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(
                con.execute("SELECT COUNT(*) FROM RACING").fetchone()[0],
                420,
            )

            row = con.execute(
                "SELECT date, course, off, horse, pos, dist_f, lbs, prize, official_rating "
                "FROM RACING WHERE horse = 'Human Evolution (IRE)' AND pos = '1'"
            ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "2026-04-28")
            self.assertEqual(row[1], "Chantilly")
            self.assertEqual(row[2], "17:00")
            self.assertEqual(row[5], 9.5)
            self.assertEqual(row[6], 130)
            self.assertAlmostEqual(row[7], 11260.87, places=2)
            self.assertEqual(row[8], 74)

            types = con.execute(
                "SELECT typeof(dist_f), typeof(lbs), typeof(prize), typeof(official_rating) "
                "FROM RACING WHERE horse = 'Human Evolution (IRE)' AND pos = '1'"
            ).fetchone()
            self.assertEqual(types, ("real", "integer", "real", "integer"))

            betfair_types = con.execute(
                "SELECT typeof(bsp), typeof(pre_min), typeof(pre_max), typeof(ip_min), "
                "typeof(ip_max), typeof(pre_vol), typeof(ip_vol) "
                "FROM RACING WHERE horse = 'Human Evolution (IRE)' AND pos = '1'"
            ).fetchone()
            self.assertEqual(betfair_types, ("null",) * 7)
        finally:
            con.close()

    def test_load_is_idempotent(self):
        bb_loader.load_csv(CSV_PATH, db_path=self.db_path)
        bb_loader.load_csv(CSV_PATH, db_path=self.db_path)
        con = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(
                con.execute("SELECT COUNT(*) FROM RACING").fetchone()[0],
                420,
            )
        finally:
            con.close()


@unittest.skipUnless(BETFAIR_CSV_PATH.exists(), f"Input CSV not present at {BETFAIR_CSV_PATH}")
class LoadCsvWithBetfairTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "BB.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_inserts_all_rows_with_betfair_columns(self):
        n = bb_loader.load_csv(BETFAIR_CSV_PATH, db_path=self.db_path)
        self.assertEqual(n, 419)

        con = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(
                con.execute("SELECT COUNT(*) FROM RACING").fetchone()[0],
                419,
            )

            row = con.execute(
                "SELECT bsp, pre_min, pre_max, ip_min, ip_max, pre_vol, ip_vol "
                "FROM RACING WHERE date = '2026-03-05' "
                "ORDER BY course, off, num LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(row)
            for value in row:
                self.assertIsInstance(value, float)

            betfair_types = con.execute(
                "SELECT typeof(bsp), typeof(pre_min), typeof(pre_max), typeof(ip_min), "
                "typeof(ip_max), typeof(pre_vol), typeof(ip_vol) "
                "FROM RACING WHERE date = '2026-03-05' "
                "ORDER BY course, off, num LIMIT 1"
            ).fetchone()
            self.assertEqual(betfair_types, ("real",) * 7)
        finally:
            con.close()

    def test_load_with_betfair_is_idempotent(self):
        bb_loader.load_csv(BETFAIR_CSV_PATH, db_path=self.db_path)
        first = sqlite3.connect(self.db_path).execute(
            "SELECT bsp, pre_vol FROM RACING WHERE date = '2026-03-05' "
            "ORDER BY course, off, num LIMIT 1"
        ).fetchone()

        bb_loader.load_csv(BETFAIR_CSV_PATH, db_path=self.db_path)
        con = sqlite3.connect(self.db_path)
        try:
            self.assertEqual(
                con.execute("SELECT COUNT(*) FROM RACING").fetchone()[0],
                419,
            )
            second = con.execute(
                "SELECT bsp, pre_vol FROM RACING WHERE date = '2026-03-05' "
                "ORDER BY course, off, num LIMIT 1"
            ).fetchone()
            self.assertEqual(first, second)
        finally:
            con.close()


if __name__ == "__main__":
    unittest.main()
