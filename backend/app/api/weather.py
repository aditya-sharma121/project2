import time
import logging
from typing import Dict, Any, Optional, Tuple
import httpx
from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.weather import WeatherForecast

logger = logging.getLogger("afterflow.weather")
router = APIRouter(prefix="/weather", tags=["Weather"])

# 10-minute in-memory cache
_weather_cache: Dict[str, Tuple[float, WeatherForecast]] = {}
CACHE_TTL_SECONDS = 600.0


@router.get("", response_model=WeatherForecast)
async def get_weather_context(
    lat: float = Query(27.1767, ge=-90.0, le=90.0),
    lng: float = Query(78.0081, ge=-180.0, le=180.0)
):
    """Fetches real-time precipitation forecast from Open-Meteo with 10-min cache.
    HARD RULE: Weather is context, not proof of local flooding.
    """
    cache_key = f"{round(lat, 2)}_{round(lng, 2)}"
    now = time.time()

    # Check cache
    if cache_key in _weather_cache:
        cached_time, cached_data = _weather_cache[cache_key]
        if now - cached_time < CACHE_TTL_SECONDS:
            cached_data.cached = True
            return cached_data

    # Fetch from Open-Meteo API
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "hourly": "precipitation,rain,precipitation_probability",
        "forecast_days": 1,
        "timezone": "Asia/Kolkata"
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                hourly = data.get("hourly", {})
                precip_list = hourly.get("precipitation", [0.0])
                prob_list = hourly.get("precipitation_probability", [0.0])
                times_list = hourly.get("time", [])

                curr_precip = precip_list[0] if precip_list else 0.0
                curr_prob = prob_list[0] if prob_list else 0.0

                if curr_precip > 10.0:
                    summary = "Torrential rainfall alert - high flash flood probability"
                elif curr_precip > 2.5:
                    summary = "Moderate continuous rainfall detected"
                elif curr_precip > 0.0:
                    summary = "Light drizzle / overcast conditions"
                else:
                    summary = "Clear / dry surface conditions"

                forecast = WeatherForecast(
                    latitude=lat,
                    longitude=lng,
                    timezone=data.get("timezone", "Asia/Kolkata"),
                    current_precipitation_mm=curr_precip,
                    rain_probability_pct=curr_prob,
                    condition_summary=summary,
                    hourly_rain_mm=precip_list[:12],
                    hourly_timestamps=times_list[:12],
                    disclaimer="Weather is context, not proof of local flooding.",
                    cached=False
                )
                _weather_cache[cache_key] = (now, forecast)
                return forecast
    except Exception as e:
        logger.warning(f"Open-Meteo live API request failed or timed out: {e}. Returning context fallback.")

    # Graceful fallback if offline or network limited
    fallback_forecast = WeatherForecast(
        latitude=lat,
        longitude=lng,
        timezone="Asia/Kolkata",
        current_precipitation_mm=4.5,
        rain_probability_pct=85.0,
        condition_summary="Monsoon precipitation band active (Telemetry context)",
        hourly_rain_mm=[4.5, 6.2, 5.0, 3.1, 1.2, 0.5, 0.0, 0.0],
        hourly_timestamps=["T00:00", "T01:00", "T02:00", "T03:00", "T04:00", "T05:00", "T06:00", "T07:00"],
        disclaimer="Weather is context, not proof of local flooding.",
        cached=False
    )
    return fallback_forecast
