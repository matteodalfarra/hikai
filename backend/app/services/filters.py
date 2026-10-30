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
        if filters.min_altitude_m is not None and trail.max_altitude_m < filters.min_altitude_m:
            continue
        if filters.area is not None and filters.area.lower() not in trail.area.lower():
            continue
        if filters.is_loop is not None and trail.is_loop != filters.is_loop:
            continue
        if filters.needs_hut and not trail.hut_names:
            continue
        results.append(trail)

    return results

def get_safety_note(filters: TrailFilters) -> str | None:
    if filters.max_difficulty is None:
        return None

    max_difficulty = get_max_difficulty(filters)
    if max_difficulty == filters.max_difficulty:
        return None

    if filters.experience is None:
        return (
            f"Difficulty limited to {max_difficulty} because the user's experience is unknown. "
            "Ask about their experience before suggesting harder trails."
        )

    return (
        f"Difficulty limited to {max_difficulty} because the user is {filters.experience}. "
        f"Explain that {filters.max_difficulty} trails are not safe for them and suggest easier ones."
    )