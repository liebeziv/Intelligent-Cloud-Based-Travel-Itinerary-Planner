import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from ..schemas.recommendation import RecommendationRequest
from .maps_service import maps_service
from .weather_service import weather_service

logger = logging.getLogger(__name__)


class ItineraryPlanner:
    """Generate day-by-day itineraries using recommendations and map data."""

    def __init__(self) -> None:
        self.maps = maps_service
        self.weather = weather_service

    def build_itinerary(
        self,
        request: RecommendationRequest,
        recommendations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not recommendations:
            return {
                "itinerary_id": str(uuid.uuid4()),
                "days": [],
                "summary": {"total_attractions": 0},
                "weather": None,
            }

        duration = max(1, request.preferences.duration)
        attractions_per_day = max(1, min(4, len(recommendations) // duration or 1))
        selected = recommendations[: duration * attractions_per_day]

        base_location: Optional[Tuple[float, float]] = None
        if request.current_location:
            base_location = (request.current_location.lat, request.current_location.lng)

        weather = None
        if base_location:
            weather = self.weather.get_current_weather(*base_location)

        itinerary_days: List[Dict[str, Any]] = []
        totals = {"distance_km": 0.0, "duration_minutes": 0.0}
        current_index = 0

        for day_index in range(1, duration + 1):
            day_items = selected[current_index : current_index + attractions_per_day]
            if not day_items:
                break

            route = self._build_daily_route(day_index, base_location, day_items)
            itinerary_days.append(route)
            totals["distance_km"] += route.get("total_distance_km", 0)
            totals["duration_minutes"] += route.get("total_duration_minutes", 0)
            current_index += attractions_per_day

        summary = {
            "total_days": len(itinerary_days),
            "total_attractions": len(selected),
            "total_distance_km": round(totals["distance_km"], 2),
            "total_travel_time_minutes": round(totals["duration_minutes"], 1),
        }

        return {
            "itinerary_id": str(uuid.uuid4()),
            "days": itinerary_days,
            "summary": summary,
            "weather": weather,
        }

    def _build_daily_route(
        self,
        day_index: int,
        start: Optional[Tuple[float, float]],
        attractions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        coords: List[Tuple[float, float]] = []
        coord_index_map: Dict[int, int] = {}
        for idx, attraction in enumerate(attractions):
            loc = attraction.get("location", {})
            lat = loc.get("lat")
            lng = loc.get("lng")
            if lat is None or lng is None:
                logger.debug("Attraction %s missing location", attraction.get("name"))
                continue
            coord_index_map[idx] = len(coords)
            coords.append((lat, lng))

        origins: List[Tuple[float, float]] = []
        destinations: List[Tuple[float, float]] = []
        if coords:
            if start:
                origins = [start] + coords[:-1]
            else:
                origins = coords[:-1]
            destinations = coords

        travel_matrix = None
        if self.maps.is_configured() and origins and destinations:
            travel_matrix = self.maps.distance_matrix(origins, destinations)

        segments: List[Dict[str, Any]] = []
        total_distance = 0.0
        total_duration = 0.0
        start_time = datetime.datetime.combine(
            datetime.date.today(), datetime.time(hour=9, minute=0)
        )

        for idx, attraction in enumerate(attractions):
            travel_info = self._resolve_segment_travel(idx, coords, coord_index_map, start, travel_matrix)

            if travel_info.get("distance_km") is not None:
                total_distance += travel_info["distance_km"]
            if travel_info.get("duration_minutes") is not None:
                total_duration += travel_info["duration_minutes"]

            arrival = start_time + datetime.timedelta(minutes=total_duration)
            leave = arrival + datetime.timedelta(hours=2)

            segments.append(
                {
                    "attraction": attraction,
                    "travel": travel_info,
                    "arrival_time": arrival.isoformat(),
                    "departure_time": leave.isoformat(),
                }
            )

        day_date = datetime.date.today() + datetime.timedelta(days=day_index - 1)
        return {
            "day_index": day_index,
            "date": day_date.isoformat(),
            "segments": segments,
            "total_distance_km": round(total_distance, 2),
            "total_duration_minutes": round(total_duration, 1),
        }

    def _resolve_segment_travel(
        self,
        attraction_idx: int,
        coords: List[Tuple[float, float]],
        coord_index_map: Dict[int, int],
        start: Optional[Tuple[float, float]],
        travel_matrix: Optional[List[List[Dict[str, float]]]],
    ) -> Dict[str, Optional[float]]:
        coord_idx = coord_index_map.get(attraction_idx)
        if coord_idx is None or coord_idx >= len(coords):
            return {"distance_km": None, "duration_minutes": None}

        if travel_matrix and coord_idx < len(travel_matrix):
            row = travel_matrix[coord_idx]
            if coord_idx < len(row):
                result = row[coord_idx]
                if result:
                    return result

        previous_point: Optional[Tuple[float, float]] = None
        if coord_idx == 0:
            previous_point = start
        elif coord_idx - 1 < len(coords):
            previous_point = coords[coord_idx - 1]

        if not previous_point:
            return {"distance_km": None, "duration_minutes": None}

        distance = self.maps.haversine_distance(previous_point, coords[coord_idx])
        estimated_speed_kmh = 50.0
        duration = round((distance / estimated_speed_kmh) * 60, 1) if distance is not None else None
        return {"distance_km": distance, "duration_minutes": duration}


itinerary_planner = ItineraryPlanner()

