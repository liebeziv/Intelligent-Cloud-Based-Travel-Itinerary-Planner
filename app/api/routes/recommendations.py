# Recommendation System API Routing

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from ...services.recommendation_service import RecommendationService
from ...schemas.recommendation import RecommendationRequest, RecommendationResponse, UserPreferences, LocationInfo
from ...data.sample_attractions import SAMPLE_NZ_ATTRACTIONS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

# Create and initialize recommendation service
recommendation_service = RecommendationService()

async def init_recommendation_service():
    if not recommendation_service.is_initialized:
        try:
            # Try to load configured open-data sources first, then fall back to sample data
            from ...services.open_data_service import load_default_sources
            open_data = load_default_sources()
            if open_data:
                await recommendation_service.initialize(open_data)
                logger.info(f"Recommendation service initialized with {len(open_data)} open-data attractions")
            else:
                from ...data.sample_attractions import SAMPLE_NZ_ATTRACTIONS
                await recommendation_service.initialize(SAMPLE_NZ_ATTRACTIONS)
                logger.info("Recommendation service initialized with sample data")
        except Exception as e:
            logger.error(f"Failed during recommendation service initialization: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize recommendation service")

async def get_recommendation_service() -> RecommendationService:
    await init_recommendation_service()
    return recommendation_service

@router.post("/")
async def get_recommendations(request: dict, service: RecommendationService = Depends(get_recommendation_service)):
    """Get personalized recommendations"""
    try:
        # Log received request data
        logger.info(f"Received recommendation request: {request}")

        # Ensure preferences contain necessary fields
        preferences = request.get("preferences", {})
        if not preferences.get("activity_types"):
            preferences["activity_types"] = ["natural", "scenic"]  # Default activity types
        
        # Convert request to RecommendationRequest model
        recommendation_request = RecommendationRequest(
            user_id=request.get("user_id", "test_user"),
            preferences=UserPreferences(**preferences),
            current_location=LocationInfo(**request.get("current_location", {})) if request.get("current_location") else None,
            exclude_visited=request.get("exclude_visited", []),
            top_k=request.get("top_k", 6)
        )
        
        # Get recommendations
        response = await service.get_recommendations(recommendation_request)
        
        # Log recommendation results
        logger.info(f"Generated {len(response.recommendations)} recommendations")
        
        return response
    except ValueError as ve:
        logger.warning(f"Invalid request parameters: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/initialize")
async def initialize_recommendations(
    attractions_data: List[Dict[str, Any]],
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Initialize recommendation system with attraction data"""
    try:
        await service.initialize(attractions_data)
        return {"status": "success", "message": f"Recommendation system initialized successfully, loaded {len(attractions_data)} attractions"}
    except Exception as e:
        logger.error(f"Failed to initialize recommendation system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
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