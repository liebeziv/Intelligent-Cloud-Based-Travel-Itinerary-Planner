

# Recommended System API Routing


from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from ...services.recommendation_service import RecommendationService
from ...schemas.recommendation import RecommendationRequest, RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


recommendation_service = RecommendationService()

async def get_recommendation_service() -> RecommendationService:
   
    return recommendation_service

@router.post("/")
async def get_recommendations(request: dict):
    """Simplified recommendation endpoint"""
    
  
    return {
        "user_id": request.get("user_id", "test_user"),
        "recommendations": [
            {
                "id": "001",
                "name": "Milford Sound",
                "category": "natural",
                "rating": 4.8,
                "description": "Stunning fjord with waterfalls",
                "location": {"lat": -44.6, "lng": 167.9},
                "price_range": [100, 300],
                "confidence_score": 0.9,
                "reasons": ["Matches your interest in natural attractions"]
            },
            {
                "id": "002",
                "name": "Hobbiton Movie Set", 
                "category": "cultural",
                "rating": 4.7,
                "description": "Movie set from Lord of the Rings",
                "location": {"lat": -37.8, "lng": 175.7},
                "price_range": [80, 120],
                "confidence_score": 0.8,
                "reasons": ["Popular tourist attraction"]
            }
        ],
        "total_found": 2,
        "request_id": f"req_{request.get('user_id', 'test')}"
    }
    
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