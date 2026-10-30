from typing import Literal

from pydantic import BaseModel

from app.schemas.trail import Difficulty

class TrailFilters(BaseModel):
    experience: Literal["beginner", "intermediate", "expert"] | None = None
    max_difficulty: Difficulty | None = None
    max_duration_min: int | None = None
    max_elevation_gain_m: int | None = None
    area: str | None = None
    is_loop: bool | None = None
    needs_hut: bool = False