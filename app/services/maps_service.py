import logging
from typing import Dict, List, Optional, Tuple

import requests

from ..config import settings
from ..security.secrets_manager import get_api_keys

logger = logging.getLogger(__name__)


class MapsService:
    """Interact with Google Maps Distance Matrix API to estimate travel times."""

    def __init__(self) -> None:
        api_keys = get_api_keys()
        self.api_key = settings.GOOGLE_MAPS_API_KEY or api_keys.get("maps")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def distance_matrix(
        self,
        origins: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]],
        mode: str = "driving",
    ) -> Optional[List[List[Dict[str, float]]]]:
        if not self.api_key:
            logger.warning("Google Maps API key not configured")
            return None

        params = {
            "origins": "|".join(f"{lat},{lng}" for lat, lng in origins),
            "destinations": "|".join(f"{lat},{lng}" for lat, lng in destinations),
            "key": self.api_key,
            "mode": mode,
        }

        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            logger.error("Google Distance Matrix error: %s", exc)
            return None

        if payload.get("status") != "OK":
            logger.error("Distance Matrix API returned status %s", payload.get("status"))
            return None

        matrix: List[List[Dict[str, float]]] = []
        for row in payload.get("rows", []):
            elements: List[Dict[str, float]] = []
            for element in row.get("elements", []):
                if element.get("status") != "OK":
                    elements.append({"distance_km": None, "duration_minutes": None})
                else:
                    distance_m = element.get("distance", {}).get("value", 0)
                    duration_s = element.get("duration", {}).get("value", 0)
                    elements.append({
                        "distance_km": round(distance_m / 1000, 2),
                        "duration_minutes": round(duration_s / 60, 1),
                    })
            matrix.append(elements)
        return matrix

    @staticmethod
    def haversine_distance(origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
        """Fallback distance calculation in kilometers."""
        from math import radians, cos, sin, asin, sqrt

        lat1, lon1 = origin
        lat2, lon2 = destination
        lon_diff = radians(lon2 - lon1)
        lat_diff = radians(lat2 - lat1)

        a = sin(lat_diff / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(lon_diff / 2) ** 2
        c = 2 * asin(sqrt(a))
        radius_earth_km = 6371
        return round(radius_earth_km * c, 2)


maps_service = MapsService()
