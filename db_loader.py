"""
Loads the 4 JSON files in /home/pete/projects/BB/DATA/ into racing.db.

Assumes racing.db has been created by db_schema.py (KAN-23).
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path("/home/pete/projects/BB/DATA/racing.db")
DATA_DIR = Path("/home/pete/projects/BB/DATA")


class RacingDataLoader:

    def __init__(self, db_path: Path = DB_PATH, data_dir: Path = DATA_DIR):
        self.db_path = db_path
        self.data_dir = data_dir
        self.con = sqlite3.connect(db_path)
        self.con.execute("PRAGMA foreign_keys = ON")

    # ---- helpers ------------------------------------------------------

    def _load_json(self, filename: str) -> Any:
        return json.loads((self.data_dir / filename).read_text())

    def _course_id_for(self, course_name: str) -> Optional[str]:
        row = self.con.execute(
            "SELECT course_id FROM courses WHERE name = ?", (course_name,)
        ).fetchone()
        return row[0] if row else None

    def _upsert_horse(self, cur, runner: dict) -> None:
        horse_id = runner.get("horse_id")
        if not horse_id:
            return
        cur.execute(
            """INSERT OR REPLACE INTO horses (
                horse_id, name, age, sex, sex_code, colour, region,
                dam, dam_id, sire, sire_id, damsire, damsire_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                horse_id,
                runner.get("horse"),
                runner.get("age"),
                runner.get("sex"),
                runner.get("sex_code"),
                runner.get("colour"),
                runner.get("region"),
                runner.get("dam"),
                self._nn(runner.get("dam_id")),
                runner.get("sire"),
                self._nn(runner.get("sire_id")),
                runner.get("damsire"),
                self._nn(runner.get("damsire_id")),
            ),
        )

    def _upsert_jockey(self, cur, runner: dict) -> None:
        jid = runner.get("jockey_id")
        if not jid:
            return
        cur.execute(
            "INSERT OR REPLACE INTO jockeys (jockey_id, name) VALUES (?, ?)",
            (jid, runner.get("jockey")),
        )

    def _upsert_trainer(self, cur, runner: dict) -> None:
        tid = runner.get("trainer_id")
        if not tid:
            return
        cur.execute(
            "INSERT OR REPLACE INTO trainers (trainer_id, name) VALUES (?, ?)",
            (tid, runner.get("trainer")),
        )

    def _upsert_owner(self, cur, runner: dict) -> None:
        oid = runner.get("owner_id")
        if not oid:
            return
        cur.execute(
            "INSERT OR REPLACE INTO owners (owner_id, name) VALUES (?, ?)",
            (oid, runner.get("owner")),
        )

    def _upsert_race(self, cur, race: dict, source: str) -> None:
        """source is 'racecard' or 'result'."""
        if source == "racecard":
            off_time = race.get("off_time")
            distance_f = race.get("distance_f")
            race_class = race.get("race_class")
            sex_restriction = race.get("sex_restriction")
            field_size = race.get("field_size")
            prize = race.get("prize")
        else:  # result
            off_time = race.get("off")
            distance_f = race.get("dist_f")
            race_class = race.get("class")
            sex_restriction = race.get("sex_rest")
            field_size = None
            prize = None

        cur.execute(
            """INSERT OR REPLACE INTO races (
                race_id, course_id, date, off_time, off_dt, race_name,
                distance_f, region, pattern, race_class, race_type,
                age_band, rating_band, sex_restriction, prize,
                going, surface, field_size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                race.get("race_id"),
                self._course_id_for(race.get("course", "")),
                race.get("date"),
                off_time,
                race.get("off_dt"),
                race.get("race_name"),
                distance_f,
                race.get("region"),
                race.get("pattern"),
                race_class,
                race.get("type"),
                race.get("age_band"),
                race.get("rating_band"),
                sex_restriction,
                prize,
                race.get("going"),
                race.get("surface"),
                int(field_size) if field_size and str(field_size).isdigit() else None,
            ),
        )

    @staticmethod
    def _nn(value):
        """Return None for falsy/empty values so FKs don't choke on empty strings."""
        return value if value else None

    def _upsert_race_entry(self, cur, race_id: str, runner: dict, source: str) -> None:
        horse_id = self._nn(runner.get("horse_id"))
        if not horse_id:
            return

        existing = cur.execute(
            "SELECT id FROM race_entries WHERE race_id = ? AND horse_id = ?",
            (race_id, horse_id),
        ).fetchone()

        if source == "racecard":
            pre_race_cols = {
                "jockey_id": self._nn(runner.get("jockey_id")),
                "trainer_id": self._nn(runner.get("trainer_id")),
                "owner_id": self._nn(runner.get("owner_id")),
                "number": runner.get("number"),
                "draw": runner.get("draw"),
                "headgear": runner.get("headgear"),
                "lbs": runner.get("lbs"),
                "ofr": runner.get("ofr"),
                "last_run": runner.get("last_run"),
                "form": runner.get("form"),
            }
            if existing:
                cur.execute(
                    """UPDATE race_entries SET
                        jockey_id=?, trainer_id=?, owner_id=?, number=?, draw=?,
                        headgear=?, lbs=?, ofr=?, last_run=?, form=?
                        WHERE id=?""",
                    (*pre_race_cols.values(), existing[0]),
                )
            else:
                cur.execute(
                    """INSERT INTO race_entries (
                        race_id, horse_id, jockey_id, trainer_id, owner_id,
                        number, draw, headgear, lbs, ofr, last_run, form
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (race_id, horse_id, *pre_race_cols.values()),
                )
        else:  # result
            post_race_cols = {
                "jockey_id": self._nn(runner.get("jockey_id")),
                "trainer_id": self._nn(runner.get("trainer_id")),
                "owner_id": self._nn(runner.get("owner_id")),
                "number": runner.get("number"),
                "draw": runner.get("draw"),
                "headgear": runner.get("headgear"),
                "position": runner.get("position"),
                "weight": runner.get("weight"),
                "weight_lbs": runner.get("weight_lbs"),
                "official_rating": runner.get("or"),
            }
            if existing:
                cur.execute(
                    """UPDATE race_entries SET
                        jockey_id=COALESCE(?, jockey_id),
                        trainer_id=COALESCE(?, trainer_id),
                        owner_id=COALESCE(?, owner_id),
                        number=COALESCE(?, number),
                        draw=COALESCE(?, draw),
                        headgear=COALESCE(?, headgear),
                        position=?, weight=?, weight_lbs=?, official_rating=?
                        WHERE id=?""",
                    (*post_race_cols.values(), existing[0]),
                )
            else:
                cur.execute(
                    """INSERT INTO race_entries (
                        race_id, horse_id, jockey_id, trainer_id, owner_id,
                        number, draw, headgear,
                        position, weight, weight_lbs, official_rating
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (race_id, horse_id, *post_race_cols.values()),
                )

    # ---- loaders ------------------------------------------------------

    def load_regions(self) -> int:
        data = self._load_json("course_regions.json")
        cur = self.con.cursor()
        for r in data:
            cur.execute(
                "INSERT OR REPLACE INTO regions (region_code, region) VALUES (?, ?)",
                (r["region_code"], r["region"]),
            )
        self.con.commit()
        return len(data)

    def load_courses(self) -> int:
        data = self._load_json("courses.json")
        courses = data.get("courses", [])
        cur = self.con.cursor()
        for c in courses:
            cur.execute(
                "INSERT OR REPLACE INTO regions (region_code, region) VALUES (?, ?)",
                (c["region_code"], c["region"]),
            )
            cur.execute(
                """INSERT OR REPLACE INTO courses (course_id, name, region_code)
                   VALUES (?, ?, ?)""",
                (c["id"], c["course"], c["region_code"]),
            )
        self.con.commit()
        return len(courses)

    def load_racecards(self) -> int:
        data = self._load_json("racecards.json")
        racecards = data.get("racecards", [])
        cur = self.con.cursor()
        for race in racecards:
            self._upsert_race(cur, race, source="racecard")
            for runner in race.get("runners", []):
                self._upsert_horse(cur, runner)
                self._upsert_jockey(cur, runner)
                self._upsert_trainer(cur, runner)
                self._upsert_owner(cur, runner)
                self._upsert_race_entry(cur, race["race_id"], runner, source="racecard")
        self.con.commit()
        return len(racecards)

    def load_results(self) -> int:
        data = self._load_json("results.json")
        results = data.get("results", [])
        cur = self.con.cursor()
        for race in results:
            self._upsert_race(cur, race, source="result")
            for runner in race.get("runners", []):
                self._upsert_horse(cur, runner)
                self._upsert_jockey(cur, runner)
                self._upsert_trainer(cur, runner)
                self._upsert_owner(cur, runner)
                self._upsert_race_entry(cur, race["race_id"], runner, source="result")
        self.con.commit()
        return len(results)

    def load_all(self) -> dict:
        counts = {
            "regions":   self.load_regions(),
            "courses":   self.load_courses(),
            "racecards": self.load_racecards(),
            "results":   self.load_results(),
        }
        return counts

    def close(self) -> None:
        self.con.close()


def main():
    loader = RacingDataLoader()
    counts = loader.load_all()
    print("Rows inserted from JSON:")
    for k, v in counts.items():
        print(f"  {k:10s} {v}")

    print("\nRow counts per table:")
    for table in ("regions", "courses", "horses", "jockeys", "trainers",
                  "owners", "races", "race_entries"):
        n = loader.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:15s} {n}")

    loader.close()


if __name__ == "__main__":
    main()
