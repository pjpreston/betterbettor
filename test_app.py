"""Unit tests for non-UI helpers in app.py (KAN-28)."""

import sqlite3
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import app
import bb_schema


class CsvPathTests(unittest.TestCase):
    def test_csv_path_for_date(self):
        self.assertEqual(
            app._csv_path_for(date(2026, 4, 28)),
            Path("/home/pete/projects/BB/DATA/RP/DATA/region/all/all/2026_04_28.csv"),
        )

    def test_csv_path_zero_pads(self):
        self.assertEqual(
            app._csv_path_for(date(2025, 1, 5)).name,
            "2025_01_05.csv",
        )


class FetchRowsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "BB.db"
        bb_schema.create_schema(self.db_path)
        con = sqlite3.connect(self.db_path)
        con.executemany(
            "INSERT INTO RACING (date, course, off, horse, jockey, pos) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("2026-04-28", "Chantilly", "17:00", "Horse A", "Jock A", "1"),
                ("2026-04-28", "Chantilly", "17:00", "Horse B", "Jock B", "2"),
                ("2026-04-29", "Newmarket", "14:00", "Horse C", "Jock C", "1"),
            ],
        )
        con.commit()
        con.close()

    def tearDown(self):
        self._tmp.cleanup()

    def test_fetch_rows_filters_by_date(self):
        with patch.object(app, "DB_PATH", self.db_path):
            df = app._fetch_rows(date(2026, 4, 28))
        self.assertEqual(len(df), 2)
        self.assertTrue((df["date"] == "2026-04-28").all())

    def test_fetch_rows_returns_all_when_filter_none(self):
        with patch.object(app, "DB_PATH", self.db_path):
            df = app._fetch_rows(None)
        self.assertEqual(len(df), 3)


class SystemPromptTests(unittest.TestCase):
    def test_includes_marker_columns(self):
        df = pd.DataFrame(
            [
                {"date": "2026-04-28", "horse": "Horse A", "pos": "1", "jockey": "Jock A"},
                {"date": "2026-04-28", "horse": "Horse B", "pos": "2", "jockey": "Jock B"},
            ]
        )
        prompt = app._build_system_prompt(df, "2026-04-28")
        self.assertIn("Horse A", prompt)
        self.assertIn("Jock B", prompt)
        self.assertIn("2026-04-28", prompt)

    def test_handles_empty(self):
        prompt = app._build_system_prompt(pd.DataFrame(), "2026-04-28")
        self.assertIn("no rows", prompt)


if __name__ == "__main__":
    unittest.main()
