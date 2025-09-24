import logging
import time
from typing import Dict, Optional, Any

import requests

from ..config import settings
from ..security.secrets_manager import get_api_keys

logger = logging.getLogger(__name__)


class WeatherService:
    """Wrapper around OpenWeather current weather API with basic caching."""

    _CACHE_TTL = 900  # seconds

    def __init__(self) -> None:
        api_keys = get_api_keys()
        self.api_key = settings.OPENWEATHER_API_KEY or api_keys.get("weather")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _build_cache_key(self, lat: float, lon: float) -> str:
        return f"{lat:.4f},{lon:.4f}"

    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return None

        cache_key = self._build_cache_key(lat, lon)
        cached = self._cache.get(cache_key)
        now = time.time()
        if cached and now - cached["timestamp"] < self._CACHE_TTL:
            return cached["data"]

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }
        url = "https://api.openweathermap.org/data/2.5/weather"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            logger.error("Weather API error: %s", exc)
            return None

        weather = self._transform_payload(payload)
        self._cache[cache_key] = {"timestamp": now, "data": weather}
        return weather

    def _transform_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        weather_main = (payload.get("weather") or [{}])[0]
        condition = weather_main.get("main", "Unknown")
        return {
            "temperature": round(payload.get("main", {}).get("temp", 0), 1),
            "feels_like": round(payload.get("main", {}).get("feels_like", 0), 1),
            "humidity": payload.get("main", {}).get("humidity"),
            "condition": condition,
            "description": weather_main.get("description", condition),
            "icon": weather_main.get("icon"),
            "wind_speed": payload.get("wind", {}).get("speed"),
            "suitable_for_outdoor": condition.lower() not in {"rain", "storm"},
            "source": "openweather",
            "timestamp": payload.get("dt"),
        }


weather_service = WeatherService()
