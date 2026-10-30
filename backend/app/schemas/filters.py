from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.trail import Difficulty

class TrailFilters(BaseModel):
    experience: Literal["beginner", "intermediate", "expert"] | None = Field(
        default=None, description="Hiking experience of the user, if mentioned"
    )
    max_difficulty: Difficulty | None = Field(
        default=None, description="Max CAI difficulty: T (easy), E (hiking), EE (expert), EEA (via ferrata)"
    )
    max_duration_min: int | None = Field(
        default=None, description="Max total duration in minutes. Half day is about 240"
    )
    max_elevation_gain_m: int | None = Field(
        default=None, description="Max elevation gain in meters. 'Not much' is about 400"
    )
    area: str | None = Field(
        default=None, description="Area name. Only set it if the user explicitly names a place"
    )
    is_loop: bool | None = Field(default=None, description="True if the user wants a loop trail")
    needs_hut: bool = Field(default=False, description="True if the user wants a mountain hut on the way")