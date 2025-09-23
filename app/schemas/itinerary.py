from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .recommendation import RecommendationRequest, AttractionRecommendation


class TravelSegment(BaseModel):
    attraction: Dict[str, Any]
    travel: Dict[str, Optional[float]]
    arrival_time: str
    departure_time: str


class DayPlan(BaseModel):
    day_index: int
    date: str
    segments: List[TravelSegment]
    total_distance_km: float
    total_duration_minutes: float


class ItineraryPlan(BaseModel):
    itinerary_id: str
    days: List[DayPlan]
    summary: Dict[str, Any]
    weather: Optional[Dict[str, Any]]
    recommendations: List[AttractionRecommendation]
    context: Optional[str] = None


class ItineraryPlanRequest(RecommendationRequest):
    save: bool = True

