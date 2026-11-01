from app.services.weather import get_weather_warnings, summarize_forecast

def make_hourly(storm_hour: int | None = None, rain: int = 0) -> dict:
    hours = range(24)
    return {
        "time": [f"2026-07-15T{hour:02d}:00" for hour in hours],
        "temperature_2m": [10 + hour % 12 for hour in hours],
        "precipitation_probability": [rain for _ in hours],
        "weather_code": [95 if hour == storm_hour else 1 for hour in hours],
    }

def test_no_storm():
    summary = summarize_forecast(make_hourly())
    assert summary["storm_risk"] is False
    assert summary["thunderstorm_hours"] == []

def test_afternoon_storm():
    summary = summarize_forecast(make_hourly(storm_hour=15))
    assert summary["storm_risk"] is True
    assert summary["thunderstorm_hours"] == [15]

def test_morning_storm_is_not_afternoon():
    summary = summarize_forecast(make_hourly(storm_hour=9))
    assert summary["thunderstorm_hours"] == []

def test_high_rain_is_a_risk():
    summary = summarize_forecast(make_hourly(rain=70))
    assert summary["storm_risk"] is True

def test_min_and_max_temperature():
    summary = summarize_forecast(make_hourly())
    assert summary["min_temp_c"] == 10
    assert summary["max_temp_c"] == 21

def test_cold_warning():
    summary = {"storm_risk": False, "min_temp_c": -3}
    warnings = get_weather_warnings(summary)
    assert len(warnings) == 1
    assert "freezing" in warnings[0]

def test_storm_and_cold_warnings():
    summary = {"storm_risk": True, "min_temp_c": -1}
    assert len(get_weather_warnings(summary)) == 2


def test_no_warnings():
    summary = {"storm_risk": False, "min_temp_c": 8}
    assert get_weather_warnings(summary) == []
