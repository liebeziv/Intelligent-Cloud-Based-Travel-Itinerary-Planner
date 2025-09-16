
# Recommended Service Layer


from typing import List, Dict, Any, Optional
import logging
from ..core.recommendation import HybridRecommender
from ..schemas.recommendation import (
    RecommendationRequest, 
    RecommendationResponse, 
    AttractionRecommendation
)

logger = logging.getLogger(__name__)

class RecommendationService:
    # Recommended Service Layer
    
    def __init__(self):
        self.recommender = HybridRecommender()
        self._attractions_cache = []
        self.is_initialized = False
        
    async def initialize(self, attractions_data: List[Dict[str, Any]]):
        # Initialize the service
        try:
            await self.recommender.load_data(attractions_data)
            self._attractions_cache = attractions_data
            self.is_initialized = True
            logger.info(f"Recommendation service initialised successfully, loaded {len(attractions_data)} attractions")
        except Exception as e:
            logger.error(f"Recommendation service initialisation failed: {str(e)}")
            raise
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        # Get personalized recommendations
        if not self.is_initialized:
            raise ValueError("Recommendation service not initialized, please call initialize method first")

        try:
            # Prepare recommendation parameters
            recommend_kwargs = {
                'preferences': request.preferences.dict(),
                'current_location': request.current_location.dict() if request.current_location else None,
                'exclude_visited': request.exclude_visited,
                'top_k': request.top_k,
                'weather': await self._get_weather_context(request.current_location)
            }

            # Get recommendation results
            raw_recommendations = await self.recommender.recommend(
                request.user_id, 
                **recommend_kwargs
            )

            # Convert to detailed recommendation results
            detailed_recommendations = []
            for attraction_id, score in raw_recommendations:
                attraction_info = self._find_attraction_by_id(attraction_id)
                if attraction_info:
                    recommendation = AttractionRecommendation(
                        attraction_id=attraction_id,
                        name=attraction_info.get('name', 'Unknown Attraction'),
                        score=round(score, 3),
                        reasons=self._generate_reasons(attraction_info, request.preferences),
                        distance=self._calculate_distance_to_user(
                            attraction_info, 
                            request.current_location
                        ),
                        estimated_time=attraction_info.get('estimated_duration', '2-3 hours'),
                        weather_suitable=True
                    )
                    detailed_recommendations.append(recommendation)
            
            return RecommendationResponse(
                recommendations=detailed_recommendations,
                total_count=len(detailed_recommendations),
                algorithm_used="hybrid",
                context={
                    "user_preferences": request.preferences.dict(),
                    "location_provided": request.current_location is not None,
                    "excluded_count": len(request.exclude_visited)
                }
            )
            
        except Exception as e:
            logger.error(f"Error occurred while generating recommendations: {str(e)}")
            return RecommendationResponse(
                recommendations=[],
                total_count=0,
                algorithm_used="error",
                context={"error": str(e)}
            )
    
    def _find_attraction_by_id(self, attraction_id: str) -> Optional[Dict[str, Any]]:
        # Find attraction information by ID
        for attraction in self._attractions_cache:
            if attraction.get('id') == attraction_id or str(hash(attraction['name'])) == attraction_id:
                return attraction
        return None
    
    def _generate_reasons(self, attraction: Dict[str, Any], preferences) -> List[str]:
        # Generate recommendation reasons
        reasons = []
        
        # Matching based on activity type
        attraction_categories = attraction.get('categories', [])
        user_activities = preferences.activity_types
        
        matching_activities = set(attraction_categories) & set(user_activities)
        if matching_activities:
            reasons.append(f"Fits your interests: {', '.join(matching_activities)}")

        # Matching based on rating
        rating = attraction.get('rating', {})
        if isinstance(rating, dict):
            avg_rating = rating.get('average', 0)
            if avg_rating >= 4.5:
                reasons.append(f"High-rated attraction ({avg_rating}/5.0)")

        # Matching based on popularity
        review_count = attraction.get('review_count', 0)
        if review_count > 1000:
            reasons.append("Popular attraction with many reviews")

        return reasons or ["Based on your preferences"]

    def _calculate_distance_to_user(self, attraction: Dict[str, Any], user_location: Optional[object]) -> Optional[float]:
        # Calculate distance to user
        if not user_location or 'location' not in attraction:
            return None
            
        attraction_location = attraction['location']
        if 'lat' not in attraction_location or 'lng' not in attraction_location:
            return None
            
        import math
        R = 6371  # Earth radius in kilometers

        lat1 = math.radians(user_location.lat)
        lat2 = math.radians(attraction_location['lat'])
        delta_lat = math.radians(attraction_location['lat'] - user_location.lat)
        delta_lng = math.radians(attraction_location['lng'] - user_location.lng)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1) * math.cos(lat2) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return round(R * c, 1)
    
    async def _get_weather_context(self, location: Optional[object]) -> Dict[str, Any]:
        # Get weather context 
        if location:
            return {
                "condition": "sunny",
                "temperature": 18,
                "suitable_for_outdoor": True
            }
        return {}