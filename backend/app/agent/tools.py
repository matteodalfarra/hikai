import json

from langchain.tools import tool

from app.schemas.filters import TrailFilters
from app.services.filters import get_safety_note, search_trails
from app.services.trails import load_trails

@tool(args_schema=TrailFilters)
def search_trails_tool(**kwargs) -> str:
    """Search Dolomites hiking trails that match the given filters."""
    filters = TrailFilters(**kwargs)
    results = search_trails(load_trails(), filters)

    if results:
        trails = [trail.model_dump(exclude={"start_point"}) for trail in results]
        text = json.dumps(trails)
    else:
        text = "No trails found with these filters."    

    note = get_safety_note(filters)
    if note:
        text += f"\n\nSafety note: {note}"

    return text