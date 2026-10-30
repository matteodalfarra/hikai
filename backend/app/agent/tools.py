import json

from langchain.tools import tool

from app.schemas.filters import TrailFilters
from app.services.filters import search_trails
from app.services.trails import load_trails

@tool(args_schema=TrailFilters)
def search_trails_tool(**kwargs) -> str:
    """Search Dolomites hiking trails that match the given filters."""
    filters = TrailFilters(**kwargs)
    results = search_trails(load_trails(), filters)

    if not results:
        return "No trails found with these filters."

    trails = [trail.model_dump(exclude={"start_point"}) for trail in results]
    return json.dumps(trails)