"""
Python library for theracingapi.com API.
One function per endpoint. Results are saved as JSON files to /home/pete/projects/BB/DATA/.
Set RACING_API_USERNAME and RACING_API_PASSWORD environment variables for auth.
"""
from dotenv import load_dotenv
import json
import os
import requests
from pathlib import Path

load_dotenv(override=True)

BASE_URL = "https://api.theracingapi.com"
DATA_DIR = Path("/home/pete/projects/BB/DATA/TODAY")

DATA_DIR.mkdir(parents=True, exist_ok=True)


def _auth():
    username = os.environ.get("RACING_API_KEY", "")
    password = os.environ.get("RACING_API_PWD", "")
    return (username, password)


def _get(path: str, params: dict = None) -> dict:
    print("_get : ", str, params)
    response = requests.get(f"{BASE_URL}{path}", auth=_auth(), params=params or {})
    response.raise_for_status()
    return response.json()


def _save(filename: str, data: dict) -> Path:
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2))
    return path


# ---------------------------------------------------------------------------
# Courses
# free plan
# ---------------------------------------------------------------------------

def get_course_regions() -> list:
    data = _get("/v1/courses/regions")
    _save("course_regions.json", data)
    return data

def get_courses(region_codes: list[str] = None) -> dict:
    params = {}
    if region_codes:
        params["region_codes"] = ",".join(region_codes)
    data = _get("/v1/courses", params)
    _save("courses.json", data)
    return data


# ---------------------------------------------------------------------------
# Racecards & Results
# free plan
# ---------------------------------------------------------------------------

def get_racecards(**kwargs) -> dict:
    data = _get("/v1/racecards/free", kwargs)
    _save("racecards.json", data)
    return data


def get_results(**kwargs) -> dict:
    data = _get("/v1/results/today/free", kwargs)
    _save("results.json", data)
    return data


# ---------------------------------------------------------------------------
# Horses
# ---------------------------------------------------------------------------

"""
def search_horses(name: str) -> dict:
    data = _get("/v1/horses/search", {"name": name})
    _save(f"horses_search_{name.replace(' ', '_')}.json", data)
    return data


def get_horse_results(horse_id: str, **kwargs) -> dict:
    data = _get(f"/v1/horses/{horse_id}/results", kwargs)
    _save(f"horse_{horse_id}_results.json", data)
    return data


def get_horse_analysis_classes(horse_id: str, **kwargs) -> dict:
    data = _get(f"/v1/horses/{horse_id}/analysis/classes", kwargs)
    _save(f"horse_{horse_id}_analysis_classes.json", data)
    return data


def get_horse_analysis_distances(horse_id: str, **kwargs) -> dict:
    data = _get(f"/v1/horses/{horse_id}/analysis/distances", kwargs)
    _save(f"horse_{horse_id}_analysis_distances.json", data)
    return data
"""

# ---------------------------------------------------------------------------
# Jockeys
# ---------------------------------------------------------------------------
"""
def search_jockeys(name: str) -> dict:
    data = _get("/v1/jockeys/search", {"name": name})
    _save(f"jockeys_search_{name.replace(' ', '_')}.json", data)
    return data


def get_jockey_results(jockey_id: str, **kwargs) -> dict:
    data = _get(f"/v1/jockeys/{jockey_id}/results", kwargs)
    _save(f"jockey_{jockey_id}_results.json", data)
    return data


def get_jockey_analysis_classes(jockey_id: str, **kwargs) -> dict:
    data = _get(f"/v1/jockeys/{jockey_id}/analysis/classes", kwargs)
    _save(f"jockey_{jockey_id}_analysis_classes.json", data)
    return data


def get_jockey_analysis_distances(jockey_id: str, **kwargs) -> dict:
    data = _get(f"/v1/jockeys/{jockey_id}/analysis/distances", kwargs)
    _save(f"jockey_{jockey_id}_analysis_distances.json", data)
    return data
"""

# ---------------------------------------------------------------------------
# Trainers
# ---------------------------------------------------------------------------
"""
def search_trainers(name: str) -> dict:
    data = _get("/v1/trainers/search", {"name": name})
    _save(f"trainers_search_{name.replace(' ', '_')}.json", data)
    return data


def get_trainer_results(trainer_id: str, **kwargs) -> dict:
    data = _get(f"/v1/trainers/{trainer_id}/results", kwargs)
    _save(f"trainer_{trainer_id}_results.json", data)
    return data


def get_trainer_analysis_classes(trainer_id: str, **kwargs) -> dict:
    data = _get(f"/v1/trainers/{trainer_id}/analysis/classes", kwargs)
    _save(f"trainer_{trainer_id}_analysis_classes.json", data)
    return data


def get_trainer_analysis_distances(trainer_id: str, **kwargs) -> dict:
    data = _get(f"/v1/trainers/{trainer_id}/analysis/distances", kwargs)
    _save(f"trainer_{trainer_id}_analysis_distances.json", data)
    return data

"""

# ---------------------------------------------------------------------------
# Owners
# ---------------------------------------------------------------------------
"""
def search_owners(name: str) -> dict:
    data = _get("/v1/owners/search", {"name": name})
    _save(f"owners_search_{name.replace(' ', '_')}.json", data)
    return data


def get_owner_results(owner_id: str, **kwargs) -> dict:
    data = _get(f"/v1/owners/{owner_id}/results", kwargs)
    _save(f"owner_{owner_id}_results.json", data)
    return data


def get_owner_analysis_classes(owner_id: str, **kwargs) -> dict:
    data = _get(f"/v1/owners/{owner_id}/analysis/classes", kwargs)
    _save(f"owner_{owner_id}_analysis_classes.json", data)
    return data


def get_owner_analysis_distances(owner_id: str, **kwargs) -> dict:
    data = _get(f"/v1/owners/{owner_id}/analysis/distances", kwargs)
    _save(f"owner_{owner_id}_analysis_distances.json", data)
    return data
"""

# ---------------------------------------------------------------------------
# Sires
# ---------------------------------------------------------------------------
"""
def search_sires(name: str) -> dict:
    data = _get("/v1/sires/search", {"name": name})
    _save(f"sires_search_{name.replace(' ', '_')}.json", data)
    return data


def get_sire_results(sire_id: str, **kwargs) -> dict:
    data = _get(f"/v1/sires/{sire_id}/results", kwargs)
    _save(f"sire_{sire_id}_results.json", data)
    return data


def get_sire_analysis_classes(sire_id: str, **kwargs) -> dict:
    data = _get(f"/v1/sires/{sire_id}/analysis/classes", kwargs)
    _save(f"sire_{sire_id}_analysis_classes.json", data)
    return data


def get_sire_analysis_distances(sire_id: str, **kwargs) -> dict:
    data = _get(f"/v1/sires/{sire_id}/analysis/distances", kwargs)
    _save(f"sire_{sire_id}_analysis_distances.json", data)
    return data
"""

# ---------------------------------------------------------------------------
# Dams
# ---------------------------------------------------------------------------
"""
def search_dams(name: str) -> dict:
    data = _get("/v1/dams/search", {"name": name})
    _save(f"dams_search_{name.replace(' ', '_')}.json", data)
    return data


def get_dam_results(dam_id: str, **kwargs) -> dict:
    data = _get(f"/v1/dams/{dam_id}/results", kwargs)
    _save(f"dam_{dam_id}_results.json", data)
    return data


def get_dam_analysis_classes(dam_id: str, **kwargs) -> dict:
    data = _get(f"/v1/dams/{dam_id}/analysis/classes", kwargs)
    _save(f"dam_{dam_id}_analysis_classes.json", data)
    return data


def get_dam_analysis_distances(dam_id: str, **kwargs) -> dict:
    data = _get(f"/v1/dams/{dam_id}/analysis/distances", kwargs)
    _save(f"dam_{dam_id}_analysis_distances.json", data)
    return data
"""

# ---------------------------------------------------------------------------
# Damsires
# ---------------------------------------------------------------------------
"""
def search_damsires(name: str) -> dict:
    data = _get("/v1/damsires/search", {"name": name})
    _save(f"damsires_search_{name.replace(' ', '_')}.json", data)
    return data


def get_damsire_results(damsire_id: str, **kwargs) -> dict:
    data = _get(f"/v1/damsires/{damsire_id}/results", kwargs)
    _save(f"damsire_{damsire_id}_results.json", data)
    return data


def get_damsire_analysis_classes(damsire_id: str, **kwargs) -> dict:
    data = _get(f"/v1/damsires/{damsire_id}/analysis/classes", kwargs)
    _save(f"damsire_{damsire_id}_analysis_classes.json", data)
    return data


def get_damsire_analysis_distances(damsire_id: str, **kwargs) -> dict:
    data = _get(f"/v1/damsires/{damsire_id}/analysis/distances", kwargs)
    _save(f"damsire_{damsire_id}_analysis_distances.json", data)
    return data
"""