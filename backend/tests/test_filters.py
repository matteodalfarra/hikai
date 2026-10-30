from app.schemas.filters import TrailFilters
from app.schemas.trail import Trail
from app.services.filters import search_trails

def make_trail(id: str, **fields) -> Trail:
    data = {
        "id": id,
        "name": id,
        "area": "Sella",
        "difficulty": "E",
        "duration_min": 120,
        "elevation_gain_m": 300,
        "distance_km": 5.0,
        "is_loop": False,
        "hut_names": [],
        "start_point": {"lat": 46.5, "lon": 11.8},
        "description": "",
    }
    data.update(fields)
    return Trail(**data)

def ids(trails: list[Trail]) -> list[str]:
    return [trail.id for trail in trails]

TRAILS = [
    make_trail("easy", difficulty="T"),
    make_trail("normal", difficulty="E"),
    make_trail("expert", difficulty="EE"),
    make_trail("ferrata", difficulty="EEA"),
]

def test_unknown_experience_hides_ee_and_eea():
    result = search_trails(TRAILS, TrailFilters())
    assert ids(result) == ["easy", "normal"]

def test_beginner_never_gets_ferrata():
    filters = TrailFilters(experience="beginner", max_difficulty="EEA")
    result = search_trails(TRAILS, filters)
    assert "expert" not in ids(result)
    assert "ferrata" not in ids(result)

def test_expert_can_get_ferrata():
    result = search_trails(TRAILS, TrailFilters(experience="expert"))
    assert "ferrata" in ids(result)

def test_max_difficulty_lower_than_experience():
    filters = TrailFilters(experience="expert", max_difficulty="T")
    assert ids(search_trails(TRAILS, filters)) == ["easy"]

def test_max_duration():
    trails = [make_trail("short", duration_min=60), make_trail("long", duration_min=300)]
    result = search_trails(trails, TrailFilters(max_duration_min=180))
    assert ids(result) == ["short"]

def test_max_elevation_gain():
    trails = [make_trail("flat", elevation_gain_m=100), make_trail("steep", elevation_gain_m=900)]
    result = search_trails(trails, TrailFilters(max_elevation_gain_m=500))
    assert ids(result) == ["flat"]

def test_area_is_case_insensitive():
    trails = [make_trail("cortina", area="Cortina / Sorapiss"), make_trail("sella", area="Sella")]
    result = search_trails(trails, TrailFilters(area="cortina"))
    assert ids(result) == ["cortina"]

def test_loop_only():
    trails = [make_trail("loop", is_loop=True), make_trail("line", is_loop=False)]
    result = search_trails(trails, TrailFilters(is_loop=True))
    assert ids(result) == ["loop"]

def test_needs_hut():
    trails = [make_trail("hut", hut_names=["Rifugio Pisciadu"]), make_trail("no-hut")]
    result = search_trails(trails, TrailFilters(needs_hut=True))
    assert ids(result) == ["hut"]
