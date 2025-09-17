
# Recommender System Data Model


from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class UserPreferences(BaseModel):
    # user preference model
    activity_types: List[str] = Field(..., description="Preferred type of activity", example=["natural", "cultural", "adventure"])
    budget_range: List[float] = Field(default=[50, 500], description="Budget range [min, max]", example=[50, 500])
    travel_style: str = Field(default="balanced", description="Travel style", example="adventure")
    difficulty_preference: str = Field(default="medium", description="Difficulty preference", example="easy")
    max_travel_distance: float = Field(default=200, description="Maximum travel distance (km)")
    group_size: int = Field(default=2, description="Group size")
    duration: int = Field(default=7, description="Duration (days)")

class LocationInfo(BaseModel):
    # Location information model
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    address: Optional[str] = Field(None, description="Address description")

class RecommendationRequest(BaseModel):
    # Recommendation request model
    user_id: str = Field(..., description="User ID")
    preferences: UserPreferences = Field(..., description="User preferences")
    current_location: Optional[LocationInfo] = Field(None, description="Current location")
    exclude_visited: List[str] = Field(default=[], description="Exclude visited attraction IDs")
    top_k: int = Field(default=10, description="Number of recommendations")

class AttractionRecommendation(BaseModel):
    # Attraction recommendation result
    attraction_id: str = Field(..., description="Attraction ID")
    name: str = Field(..., description="Attraction name")
    score: float = Field(..., description="Recommendation score")
    reasons: List[str] = Field(default=[], description="Reasons for recommendation")
    distance: Optional[float] = Field(None, description="Distance (km)")
    estimated_time: Optional[str] = Field(None, description="Estimated visit time")
    weather_suitable: bool = Field(default=True, description="Is current weather suitable")

class RecommendationResponse(BaseModel):
    # Recommendation response model
    recommendations: List[AttractionRecommendation] = Field(..., description="Recommendation results")
    total_count: int = Field(..., description="Total number of recommendations")
    algorithm_used: str = Field(default="hybrid", description="Algorithm used")
    context: Dict[str, Any] = Field(default={}, description="Recommendation context information")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation time")