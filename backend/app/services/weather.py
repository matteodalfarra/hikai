import httpx

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
THUNDERSTORM_CODES = {95, 96, 99}
AFTERNOON_HOURS = range(12, 19)
RAIN_RISK_PERCENT = 50

def fetch_hourly_forecast(lat: float, lon: float, day: str) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "timezone": "Europe/Rome",
        "start_date": day,
        "end_date": day,
    }
    response = httpx.get(FORECAST_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["hourly"]

def summarize_forecast(hourly: dict) -> dict:
    storm_hours = []
    max_rain = 0

    for i, time in enumerate(hourly["time"]):
        hour = int(time[11:13])
        if hour not in AFTERNOON_HOURS:
            continue
        if hourly["weather_code"][i] in THUNDERSTORM_CODES:
            storm_hours.append(hour)
        rain = hourly["precipitation_probability"][i] or 0
        max_rain = max(max_rain, rain)

    return {
        "min_temp_c": min(hourly["temperature_2m"]),
        "max_temp_c": max(hourly["temperature_2m"]),
        "afternoon_rain_probability": max_rain,
        "thunderstorm_hours": storm_hours,
        "storm_risk": bool(storm_hours) or max_rain >= RAIN_RISK_PERCENT,
    }

def get_weather_warnings(summary: dict) -> list[str]:
    warnings = []
    if summary["storm_risk"]:
        warnings.append("Risk of afternoon thunderstorms: start early and be off exposed ridges and summits by noon.")
    if summary["min_temp_c"] <= 0:
        warnings.append("Temperatures below freezing: ice is possible on the trail, bring warm clothes.")
    return warnings
