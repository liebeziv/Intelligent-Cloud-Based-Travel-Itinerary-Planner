

# Recommended System API Routing


from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from ...services.recommendation_service import RecommendationService
from ...schemas.recommendation import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Global recommendation service instance
recommendation_service = RecommendationService()

async def get_recommendation_service() -> RecommendationService:
    # Get recommendation service instance
    return recommendation_service

@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service)
) -> RecommendationResponse:
    
    # Get personalized recommendations
    
    try:
        return await service.get_recommendations(request)
    except Exception as e:
        logger.error(f"Recommendation API error: {str(e)}")
        raise HTTPException(status_code=500, detail="Recommendation service temporarily unavailable")

@router.post("/initialize")
async def initialize_recommendations(
    attractions_data: List[Dict[str, Any]],
    service: RecommendationService = Depends(get_recommendation_service)
):
    
    # Initialize recommendation system

    # Load attraction data and train recommendation model
    
    try:
        await service.initialize(attractions_data)
        return {"status": "success", "message": f"Recommendation system initialized successfully, loaded {len(attractions_data)} attractions"}
    except Exception as e:
        logger.error(f"Failed to initialize recommendation system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.get("/health")
async def health_check():
    # Health check
    return {"status": "healthy", "service": "recommendation"}

@router.get("/sample-request")
async def get_sample_request():
    """Get sample request data for frontend development and testing"""
    return {
        "user_id": "user_12345",
        "preferences": {
            "activity_types": ["natural", "scenic", "adventure"],
            "budget_range": [100, 400],
            "travel_style": "adventure",
            "difficulty_preference": "medium",
            "max_travel_distance": 300,
            "group_size": 2,
            "duration": 7
        },
        "current_location": {
            "lat": -41.3,
            "lng": 174.8,
            "address": "Wellington, New Zealand"
        },
        "exclude_visited": ["001"],
        "top_k": 8
    }