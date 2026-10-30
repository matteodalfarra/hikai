from app.schemas.filters import TrailFilters
from app.schemas.trail import Trail

DIFFICULTY_ORDER = ["T", "E", "EE", "EEA"]

MAX_DIFFICULTY_BY_EXPERIENCE = {
    "beginner": "E",
    "intermediate": "EE",
    "expert": "EEA",
}

def get_max_difficulty(filters: TrailFilters) -> str:
    # undefined difficulty is trated as beginner
    safe_max = MAX_DIFFICULTY_BY_EXPERIENCE.get(filters.experience, "E")

    if filters.max_difficulty is None:
        return safe_max

    if (DIFFICULTY_ORDER.index(filters.max_difficulty) < DIFFICULTY_ORDER.index(safe_max)):
        return filters.max_difficulty
    return safe_max

def search_trails(trails: list[Trail], filters: TrailFilters) -> list[Trail]:
    max_level = DIFFICULTY_ORDER.index(get_max_difficulty(filters))
    results = []

    for trail in trails:
        if DIFFICULTY_ORDER.index(trail.difficulty) > max_level:
            continue
        if filters.max_duration_min is not None and trail.duration_min > filters.max_duration_min:
            continue
        if filters.max_elevation_gain_m is not None and trail.elevation_gain_m > filters.max_elevation_gain_m:
            continue
        if filters.area is not None and filters.area.lower() not in trail.area.lower():
            continue
        if filters.is_loop is not None and trail.is_loop != filters.is_loop:
            continue
        if filters.needs_hut and not trail.hut_names:
            continue
        results.append(trail)

    return results