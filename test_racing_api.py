"""Integration tests for racing_api.py — hits the REAL theracingapi.com API.

Requires RACING_API_KEY and RACING_API_PWD (loaded from environment or .env).
All tests are skipped if credentials are not configured.

Calls hit the real API, so responses are recorded as JSON files in
/home/pete/projects/BB/DATA/ just like normal use of the library.
"""

import os
import time
import unittest

from dotenv import load_dotenv

import racing_api as rapi


load_dotenv()

RATE_DELAY = 1.1  # seconds between calls (free-plan endpoints allow 1 req/s)


def _creds_present() -> bool:
    return bool(os.environ.get("RACING_API_KEY") and os.environ.get("RACING_API_PWD"))


def _extract_id(data) -> str | None:
    """Pull the first `id` out of a search response, tolerating a few shapes."""
    items = None
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in ("search_results", "results", "items", "data"):
            if isinstance(data.get(key), list):
                items = data[key]
                break
    if not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    for id_key in ("id", "horse_id", "jockey_id", "trainer_id",
                   "owner_id", "sire_id", "dam_id", "damsire_id"):
        if id_key in first:
            return str(first[id_key])
    return None


@unittest.skipUnless(_creds_present(), "RACING_API_KEY / RACING_API_PWD not set")
class TestRacingApi(unittest.TestCase):
    """Live-API tests: every racing_api function is called for real."""

    horse_id: str | None = None
    jockey_id: str | None = None
    trainer_id: str | None = None
    owner_id: str | None = None
    sire_id: str | None = None
    dam_id: str | None = None
    damsire_id: str | None = None

    @classmethod
    def setUpClass(cls):
        """Do one search per entity type up front so dependent tests have IDs."""
        """
        searches = [
            ("horse_id", rapi.search_horses, "Frankel"),
            ("jockey_id", rapi.search_jockeys, "Dettori"),
            ("trainer_id", rapi.search_trainers, "Appleby"),
            ("owner_id", rapi.search_owners, "Godolphin"),
            ("sire_id", rapi.search_sires, "Galileo"),
            ("dam_id", rapi.search_dams, "Urban Sea"),
            ("damsire_id", rapi.search_damsires, "Sadlers Wells"),
        ]
        for attr, fn, name in searches:
            try:
                setattr(cls, attr, _extract_id(fn(name)))
            except Exception:
                pass
            time.sleep(RATE_DELAY)
        """
        
    def setUp(self):
        time.sleep(RATE_DELAY)

    def _check(self, data, filename):
        self.assertIsInstance(data, (dict, list))
        self.assertTrue(
            (rapi.DATA_DIR / filename).exists(),
            f"expected {rapi.DATA_DIR / filename} to exist",
        )

    def _require(self, ident: str | None, label: str) -> str:
        if not ident:
            self.skipTest(f"no {label} available from setUpClass search")
        return ident

    # -- Courses ------------------------------------------------------------

    def test_get_course_regions(self):
        self._check(rapi.get_course_regions(), "course_regions.json")

    def test_get_courses(self):
        self._check(rapi.get_courses(), "courses.json")

    def test_get_courses_with_region_codes(self):
        self._check(rapi.get_courses(region_codes=["gb"]), "courses.json")

    # -- Racecards & Results -----------------------------------------------

    def test_get_racecards(self):
        self._check(rapi.get_racecards(), "racecards.json")

    def test_get_results(self):
        self._check(rapi.get_results(), "results.json")

    # -- Horses ------------------------------------------------------------

"""
    def test_search_horses(self):
        self._check(rapi.search_horses("Frankel"), "horses_search_Frankel.json")

    def test_get_horse_results(self):
        hid = self._require(self.horse_id, "horse_id")
        self._check(rapi.get_horse_results(hid), f"horse_{hid}_results.json")

    def test_get_horse_analysis_classes(self):
        hid = self._require(self.horse_id, "horse_id")
        self._check(
            rapi.get_horse_analysis_classes(hid),
            f"horse_{hid}_analysis_classes.json",
        )

    def test_get_horse_analysis_distances(self):
        hid = self._require(self.horse_id, "horse_id")
        self._check(
            rapi.get_horse_analysis_distances(hid),
            f"horse_{hid}_analysis_distances.json",
        )
"""
    # -- Jockeys -----------------------------------------------------------
"""
    def test_search_jockeys(self):
        self._check(rapi.search_jockeys("Dettori"), "jockeys_search_Dettori.json")

    def test_get_jockey_results(self):
        jid = self._require(self.jockey_id, "jockey_id")
        self._check(rapi.get_jockey_results(jid), f"jockey_{jid}_results.json")

    def test_get_jockey_analysis_classes(self):
        jid = self._require(self.jockey_id, "jockey_id")
        self._check(
            rapi.get_jockey_analysis_classes(jid),
            f"jockey_{jid}_analysis_classes.json",
        )

    def test_get_jockey_analysis_distances(self):
        jid = self._require(self.jockey_id, "jockey_id")
        self._check(
            rapi.get_jockey_analysis_distances(jid),
            f"jockey_{jid}_analysis_distances.json",
        )
"""
    # -- Trainers ----------------------------------------------------------
"""
    def test_search_trainers(self):
        self._check(rapi.search_trainers("Appleby"), "trainers_search_Appleby.json")

    def test_get_trainer_results(self):
        tid = self._require(self.trainer_id, "trainer_id")
        self._check(rapi.get_trainer_results(tid), f"trainer_{tid}_results.json")

    def test_get_trainer_analysis_classes(self):
        tid = self._require(self.trainer_id, "trainer_id")
        self._check(
            rapi.get_trainer_analysis_classes(tid),
            f"trainer_{tid}_analysis_classes.json",
        )

    def test_get_trainer_analysis_distances(self):
        tid = self._require(self.trainer_id, "trainer_id")
        self._check(
            rapi.get_trainer_analysis_distances(tid),
            f"trainer_{tid}_analysis_distances.json",
        )
"""
    # -- Owners ------------------------------------------------------------
"""
    def test_search_owners(self):
        self._check(rapi.search_owners("Godolphin"), "owners_search_Godolphin.json")

    def test_get_owner_results(self):
        oid = self._require(self.owner_id, "owner_id")
        self._check(rapi.get_owner_results(oid), f"owner_{oid}_results.json")

    def test_get_owner_analysis_classes(self):
        oid = self._require(self.owner_id, "owner_id")
        self._check(
            rapi.get_owner_analysis_classes(oid),
            f"owner_{oid}_analysis_classes.json",
        )

    def test_get_owner_analysis_distances(self):
        oid = self._require(self.owner_id, "owner_id")
        self._check(
            rapi.get_owner_analysis_distances(oid),
            f"owner_{oid}_analysis_distances.json",
        )
"""
    # -- Sires -------------------------------------------------------------
"""
    def test_search_sires(self):
        self._check(rapi.search_sires("Galileo"), "sires_search_Galileo.json")

    def test_get_sire_results(self):
        sid = self._require(self.sire_id, "sire_id")
        self._check(rapi.get_sire_results(sid), f"sire_{sid}_results.json")

    def test_get_sire_analysis_classes(self):
        sid = self._require(self.sire_id, "sire_id")
        self._check(
            rapi.get_sire_analysis_classes(sid),
            f"sire_{sid}_analysis_classes.json",
        )

    def test_get_sire_analysis_distances(self):
        sid = self._require(self.sire_id, "sire_id")
        self._check(
            rapi.get_sire_analysis_distances(sid),
            f"sire_{sid}_analysis_distances.json",
        )
"""
    # -- Dams --------------------------------------------------------------
"""
    def test_search_dams(self):
        self._check(rapi.search_dams("Urban Sea"), "dams_search_Urban_Sea.json")

    def test_get_dam_results(self):
        did = self._require(self.dam_id, "dam_id")
        self._check(rapi.get_dam_results(did), f"dam_{did}_results.json")

    def test_get_dam_analysis_classes(self):
        did = self._require(self.dam_id, "dam_id")
        self._check(
            rapi.get_dam_analysis_classes(did),
            f"dam_{did}_analysis_classes.json",
        )

    def test_get_dam_analysis_distances(self):
        did = self._require(self.dam_id, "dam_id")
        self._check(
            rapi.get_dam_analysis_distances(did),
            f"dam_{did}_analysis_distances.json",
        )
"""
    # -- Damsires ----------------------------------------------------------
"""
    def test_search_damsires(self):
        self._check(
            rapi.search_damsires("Sadlers Wells"),
            "damsires_search_Sadlers_Wells.json",
        )

    def test_get_damsire_results(self):
        dsid = self._require(self.damsire_id, "damsire_id")
        self._check(rapi.get_damsire_results(dsid), f"damsire_{dsid}_results.json")

    def test_get_damsire_analysis_classes(self):
        dsid = self._require(self.damsire_id, "damsire_id")
        self._check(
            rapi.get_damsire_analysis_classes(dsid),
            f"damsire_{dsid}_analysis_classes.json",
        )

    def test_get_damsire_analysis_distances(self):
        dsid = self._require(self.damsire_id, "damsire_id")
        self._check(
            rapi.get_damsire_analysis_distances(dsid),
            f"damsire_{dsid}_analysis_distances.json",
        )
"""

if __name__ == "__main__":
    unittest.main()
