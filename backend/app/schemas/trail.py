from typing import Literal

from pydantic import BaseModel

Difficulty = Literal["T", "E", "EE", "EEA"]

class Location(BaseModel):
    lat: float
    lon: float

class Trail(BaseModel):
    id: str
    name: str
    area: str
    difficulty: Difficulty
    duration_min: int
    elevation_gain_m: int
    distance_km: float
    is_loop: bool
    hut_names: list[str]
    start_point: Location
    description: str