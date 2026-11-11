import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_config():
    path = ROOT / "configs" / "default.json"
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
