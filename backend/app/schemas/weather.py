from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class WeatherForecast(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    current_precipitation_mm: float
    rain_probability_pct: float
    condition_summary: str
    hourly_rain_mm: List[float]
    hourly_timestamps: List[str]
    disclaimer: str = "Weather is context, not proof of local flooding."
    cached: bool = False
