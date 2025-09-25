import logging
import time
from typing import Dict, Optional, Any

import requests

from ..config import settings
from ..security.secrets_manager import get_api_keys


logger = logging.getLogger(__name__)


class WeatherService:
    """Wrapper around weather providers with basic caching."""

    _CACHE_TTL = 900  # seconds

    def __init__(self) -> None:
        api_keys = get_api_keys()
        self.api_key = settings.OPENWEATHER_API_KEY or api_keys.get("weather")
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _build_cache_key(self, lat: float, lon: float) -> str:
        return f"{lat:.4f},{lon:.4f}"

    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        cache_key = self._build_cache_key(lat, lon)
        cached = self._cache.get(cache_key)
        now = time.time()
        if cached and now - cached["timestamp"] < self._CACHE_TTL:
            return cached["data"]

        weather: Optional[Dict[str, Any]] = None
        if self.api_key:
            weather = self._fetch_openweather(lat, lon)

        if weather is None:
            weather = self._fetch_open_meteo(lat, lon)

        if weather is not None:
            self._cache[cache_key] = {"timestamp": now, "data": weather}

        return weather

    def _fetch_openweather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
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

        return self._transform_openweather(payload)

    def _fetch_open_meteo(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            logger.error("Open-Meteo fallback error: %s", exc)
            return None

        current = payload.get("current")
        if not current:
            return None

        return self._transform_open_meteo(current)

    def _transform_openweather(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        weather_main = (payload.get("weather") or [{}])[0]
        condition = weather_main.get("main", "Unknown")
        description = weather_main.get("description", condition)
        condition_lower = condition.lower()
        return {
            "temperature": round(payload.get("main", {}).get("temp", 0), 1),
            "feels_like": round(payload.get("main", {}).get("feels_like", 0), 1),
            "humidity": payload.get("main", {}).get("humidity"),
            "condition": condition,
            "description": description,
            "icon": weather_main.get("icon"),
            "wind_speed": payload.get("wind", {}).get("speed"),
            "suitable_for_outdoor": condition_lower not in {"rain", "storm", "snow", "thunderstorm"},
            "source": "openweather",
            "timestamp": payload.get("dt"),
        }

    def _transform_open_meteo(self, current: Dict[str, Any]) -> Dict[str, Any]:
        code = current.get("weather_code")
        condition = self._map_weather_code(code)
        description = condition
        temperature = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature", temperature)
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")
        condition_lower = condition.lower()
        return {
            "temperature": round(temperature, 1) if temperature is not None else None,
            "feels_like": round(feels_like, 1) if feels_like is not None else None,
            "humidity": humidity,
            "condition": condition,
            "description": description,
            "icon": None,
            "wind_speed": wind,
            "suitable_for_outdoor": condition_lower not in {"rain", "thunderstorm", "snow", "freezing rain"},
            "source": "open-meteo",
            "timestamp": current.get("time"),
        }

    @staticmethod
    def _map_weather_code(code: Optional[int]) -> str:
        mapping = {
            (0,): "Clear skies",
            (1, 2, 3): "Partly cloudy",
            (45, 48): "Foggy",
            (51, 53, 55): "Drizzle",
            (56, 57): "Freezing drizzle",
            (61, 63, 65): "Rain",
            (66, 67): "Freezing rain",
            (71, 73, 75): "Snow",
            (77,): "Snow grains",
            (80, 81, 82): "Rain showers",
            (85, 86): "Snow showers",
            (95,): "Thunderstorm",
            (96, 99): "Thunderstorm with hail",
        }
        for codes, label in mapping.items():
            if code in codes:
                return label
        return "Unknown"


weather_service = WeatherService()
