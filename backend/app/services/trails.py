import json
from pathlib import Path

from app.schemas.trail import Trail

DATA_PATH = Path(__file__).parents[2] / "data" / "trails.json"

def load_trails() -> list[Trail]:
    with open(DATA_PATH) as f:
        data = json.load(f)
    return [Trail(**item) for item in data]