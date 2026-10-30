import json

import httpx
from langchain.tools import tool

from app.schemas.filters import SearchTrailsInput, TrailFilters
from app.schemas.trail import Trail
from app.services.filters import get_safety_note, search_trails
from app.services.trails import load_trails
from app.services.weather import fetch_hourly_forecast, get_weather_warnings, summarize_forecast

def get_trail_weather(trail: Trail, date: str) -> dict:
    try:
        hourly = fetch_hourly_forecast(trail.start_point.lat, trail.start_point.lon, date)
    except httpx.HTTPError:
        return {"error": "Weather forecast not available for this date."}

    summary = summarize_forecast(hourly)
    summary["warnings"] = get_weather_warnings(summary)
    return summary

@tool(args_schema=SearchTrailsInput)
def search_trails_tool(**kwargs) -> str:
    """Search Dolomites hiking trails that match the given filters. If a date is given, the weather forecast is included."""
    date = kwargs.pop("date", None)
    filters = TrailFilters(**kwargs)
    results = search_trails(load_trails(), filters)

    if results:
        trails = []
        for trail in results:
            data = trail.model_dump(exclude={"start_point"})
            if date:
                data["weather"] = get_trail_weather(trail, date)
            trails.append(data)
        text = json.dumps(trails)
    else:
        text = "No trails found with these filters."

    note = get_safety_note(filters)
    if note:
        text += f"\n\nSafety note: {note}"

    return text