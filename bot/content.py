import json
from pathlib import Path
from functools import lru_cache

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

@lru_cache
def load_json(name: str):
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def principles():
    return load_json("principles.json")

def exercises():
    return load_json("exercises.json")

def cases():
    return load_json("cases.json")

def training_templates():
    return load_json("training_templates.json")

def get_exercises_by_theme(theme: str):
    rows = exercises()["exercises"]
    return [e for e in rows if theme in e.get("themes", []) or theme in e.get("tags", [])]

def get_cases_by_theme(theme: str):
    rows = cases()["cases"]
    return [c for c in rows if theme in c.get("themes", [])]

def find_exercise(exercise_id: str):
    for e in exercises()["exercises"]:
        if e["id"] == exercise_id:
            return e
    return None
