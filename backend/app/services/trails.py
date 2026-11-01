import json
from pathlib import Path

from app.schemas.trail import Trail

DATA_PATH = Path(__file__).parents[2] / "data" / "trails.json"

def load_trails() -> list[Trail]:
    with open(DATA_PATH) as f:
        data = json.load(f)
    return [Trail(**item) for item in data]

def get_trail(trail_id: str) -> Trail | None:
    for trail in load_trails():
        if trail.id == trail_id:
            return trail
    return None