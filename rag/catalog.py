import json
from pathlib import Path

def load_universities():
    path = Path(__file__).resolve().parent.parent / "data" / "universities.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
