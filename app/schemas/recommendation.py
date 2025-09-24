# Recommender System Data Model

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class UserPreferences(BaseModel):
    """User preference model"""
    activity_types: List[str] = Field(default=["natural", "scenic"], description="Preferred type of activity")
    budget_range: List[float] = Field(default=[100, 400], description="Budget range [min, max]")
    travel_style: str = Field(default="adventure", description="Travel style")
    difficulty_preference: Optional[str] = Field(default="medium", description="Difficulty preference")
    max_travel_distance: Optional[float] = Field(default=200, description="Maximum travel distance (km)")
    group_size: Optional[int] = Field(default=2, description="Group size")
    duration: Optional[int] = Field(default=7, description="Duration (days)")

class LocationInfo(BaseModel):
    """Location information model"""
    lat: float = Field(default=-41.3, description="Latitude")
    lng: float = Field(default=174.8, description="Longitude")
    address: Optional[str] = Field(default="Wellington, New Zealand", description="Address description")

class RecommendationRequest(BaseModel):
    """Recommendation request model"""
    user_id: str = Field(..., description="User ID")
    preferences: UserPreferences = Field(..., description="User preferences")
    current_location: Optional[LocationInfo] = Field(None, description="Current location")
    exclude_visited: List[str] = Field(default=[], description="Exclude visited attraction IDs")
    top_k: int = Field(default=10, description="Number of recommendations")

class AttractionRecommendation(BaseModel):
    """Attraction recommendation result"""
    id: str = Field(..., description="Attraction ID")
    name: str = Field(..., description="Attraction name")
    description: str = Field("", description="Attraction description")
    category: str = Field("", description="Main category")
    categories: List[str] = Field(default=[], description="Activity categories")
    location: Dict[str, Any] = Field(default={}, description="Location information")
    rating: float = Field(default=4.0, description="Average rating")
    confidence_score: float = Field(..., description="Confidence score")
    reasons: List[str] = Field(default=[], description="Reasons for recommendation")
    distance: Optional[float] = Field(None, description="Distance (km)")
    price_range: List[float] = Field(default=[0, 100], description="Price range [min, max]")
    estimated_time: Optional[str] = Field(None, description="Estimated visit time")
    weather_suitable: bool = Field(default=True, description="Is current weather suitable")
    features: Dict[str, Any] = Field(default={}, description="Attraction features")

class RecommendationResponse(BaseModel):
    """Recommendation response model"""
    recommendations: List[AttractionRecommendation] = Field(..., description="Recommendation results")
    total_count: int = Field(..., description="Total number of recommendations")
    algorithm_used: str = Field(default="hybrid", description="Algorithm used")
    context: Dict[str, Any] = Field(default={}, description="Recommendation context information")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation time")