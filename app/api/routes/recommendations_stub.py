from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

class Location(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None

class Preferences(BaseModel):
    activity_types: Optional[List[str]] = None
    budget_range: Optional[List[float]] = None
    travel_style: Optional[str] = None
    difficulty_preference: Optional[str] = None
    max_travel_distance: Optional[float] = None
    group_size: Optional[int] = None
    duration: Optional[int] = None

class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    preferences: Preferences
    current_location: Optional[Location] = None
    exclude_visited: List[str] = []
    top_k: int = 5

@router.post("")
def recommend(req: RecommendationRequest):
    return {
        "recommendations": [],
        "total_count": 0,
        "algorithm_used": "stub",
        "filters": {
            "max_distance_km": req.preferences.max_travel_distance
        }
    }
