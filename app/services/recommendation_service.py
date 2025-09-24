from typing import List, Dict, Any, Optional
import logging
from ..core.recommendation import HybridRecommender
from ..schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    AttractionRecommendation,
)
from .open_data_service import load_default_sources

logger = logging.getLogger(__name__)

class RecommendationService:
    """Recommendation Service Layer with Distance Filtering"""
    
    def __init__(self):
        self.recommender = HybridRecommender()
        self._attractions_cache = []
        self.is_initialized = False
        
    async def initialize(self, attractions_data: List[Dict[str, Any]]):
        """Initialize the service"""
        try:
            await self.recommender.load_data(attractions_data)
            self._attractions_cache = attractions_data
            self.is_initialized = True
            logger.info(f"Recommendation service initialized successfully, loaded {len(attractions_data)} attractions")
        except Exception as e:
            logger.error(f"Recommendation service initialization failed: {str(e)}")
            raise
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Get personalized recommendations with distance filtering"""
        if not self.is_initialized:
            logger.warning("Recommendation service not initialized, initializing now...")
            # Try to load from configured open-data sources first
            try:
                open_data = load_default_sources()
                if open_data:
                    logger.info(f"Loaded {len(open_data)} attractions from open-data sources")
                    await self.initialize(open_data)
                else:
                    from ..data.sample_attractions import SAMPLE_NZ_ATTRACTIONS
                    if not SAMPLE_NZ_ATTRACTIONS:
                        logger.error("No sample attractions data available")
                        raise ValueError("No attractions data available")
                    logger.info(f"Loading {len(SAMPLE_NZ_ATTRACTIONS)} sample attractions")
                    await self.initialize(SAMPLE_NZ_ATTRACTIONS)
            except Exception as e:
                logger.error(f"Failed to initialize recommendation service: {str(e)}")
                raise

        try:
            logger.info(f"Processing recommendation request for user {request.user_id}")
            logger.info(f"Request preferences: {request.preferences.dict()}")
            logger.info(f"Max travel distance: {request.preferences.max_travel_distance}km")

            # Prepare location data for the recommender
            current_location = None
            if request.current_location:
                current_location = {
                    'lat': request.current_location.lat,
                    'lng': request.current_location.lng,
                    'address': request.current_location.address
                }
                logger.info(f"User location: {current_location}")

            # Get recommendations from the hybrid recommender
            raw_recommendations = await self.recommender.recommend(
                user_id=request.user_id,
                preferences=request.preferences.dict(),
                current_location=current_location,
                exclude_visited=request.exclude_visited,
                top_k=request.top_k
            )

            logger.info(f"Got {len(raw_recommendations)} raw recommendations")

            # Convert to detailed recommendation results
            detailed_recommendations = []
            for attraction_id, score in raw_recommendations:
                attraction_info = self._find_attraction_by_id(attraction_id)
                if attraction_info:
                    # Calculate price range based on price level
                    price_level = attraction_info.get('features', {}).get('price_level', 3)
                    base_price = 50 * price_level
                    price_range = [base_price, base_price * 2]

                    # Extract main category
                    categories = attraction_info.get('categories', [])
                    main_category = categories[0] if categories else 'general'

                    # Calculate distance (use cached distance if available)
                    distance = attraction_info.get('_calculated_distance')
                    if distance is None and request.current_location:
                        distance = self._calculate_distance_to_user(
                            attraction_info, 
                            request.current_location
                        )

                    recommendation = AttractionRecommendation(
                        id=str(attraction_id),
                        name=attraction_info.get('name', 'Unknown Attraction'),
                        description=attraction_info.get('description', ''),
                        category=main_category,
                        categories=categories,
                        location=attraction_info.get('location', {}),
                        rating=attraction_info.get('rating', {}).get('average', 4.0),
                        confidence_score=score,
                        reasons=self._generate_reasons(attraction_info, request.preferences, distance),
                        distance=round(distance, 1) if distance else None,
                        price_range=price_range,
                        estimated_time=attraction_info.get('estimated_duration', '2-3 hours'),
                        weather_suitable=True,
                        features=attraction_info.get('features', {})
                    )
                    detailed_recommendations.append(recommendation)
                    
            logger.info(f"Generated {len(detailed_recommendations)} detailed recommendations")
            
            # Generate context message based on distance filtering
            context_message = self._generate_context_message(
                len(detailed_recommendations), 
                request.preferences.max_travel_distance,
                request.current_location.address if request.current_location else None
            )
            
            return RecommendationResponse(
                recommendations=detailed_recommendations,
                total_count=len(detailed_recommendations),
                algorithm_used="hybrid_with_distance",
                context={
                    "user_preferences": request.preferences.dict(),
                    "location_provided": request.current_location is not None,
                    "excluded_count": len(request.exclude_visited),
                    "max_distance_km": request.preferences.max_travel_distance,
                    "message": context_message
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
    
    def _generate_context_message(self, recommendation_count: int, max_distance: float, location: str) -> str:
        """Generate helpful context message for the user"""
        if recommendation_count == 0:
            return f"No attractions found within {max_distance}km of {location}. Try increasing your travel distance in More Options."
        elif recommendation_count < 5:
            return f"Found {recommendation_count} attractions within {max_distance}km. Consider expanding your search radius for more options."
        else:
            return f"Found {recommendation_count} great attractions within {max_distance}km of {location}."
    
    def _find_attraction_by_id(self, attraction_id: str) -> Optional[Dict[str, Any]]:
        """Find attraction information by ID"""
        for attraction in self._attractions_cache:
            if str(attraction.get('id')) == attraction_id:
                return attraction
        return None
    
    def _generate_reasons(self, attraction: Dict[str, Any], preferences, distance: float = None) -> List[str]:
        """Generate recommendation reasons including distance info"""
        reasons = []
        
        # Distance-based reason
        if distance is not None:
            if distance < 25:
                reasons.append(f"Close to your destination ({distance:.1f}km away)")
            elif distance < 50:
                reasons.append(f"Within easy reach ({distance:.1f}km from base)")
            else:
                reasons.append(f"Worth the {distance:.1f}km journey")
        
        # Activity type matching
        attraction_categories = attraction.get('categories', [])
        user_activities = preferences.activity_types
        
        matching_activities = set(attraction_categories) & set(user_activities)
        if matching_activities:
            reasons.append(f"Matches your interests: {', '.join(list(matching_activities)[:2])}")

        # Rating-based reasons
        rating = attraction.get('rating', {})
        if isinstance(rating, dict):
            avg_rating = rating.get('average', 0)
            if avg_rating >= 4.5:
                reasons.append(f"Highly rated attraction ({avg_rating}/5.0)")
            elif avg_rating >= 4.0:
                reasons.append(f"Great reviews ({avg_rating}/5.0)")

        # Popularity-based reasons
        review_count = attraction.get('review_count', 0)
        if review_count > 2000:
            reasons.append("Very popular destination")
        elif review_count > 1000:
            reasons.append("Popular with travelers")

        # Duration-based reasons
        estimated_time = attraction.get('estimated_duration', '')
        if 'full_day' in estimated_time.lower():
            reasons.append("Perfect for a full day adventure")
        elif 'half_day' in estimated_time.lower():
            reasons.append("Great for half-day exploration")

        return reasons[:3]  # Limit to 3 most relevant reasons

    def _calculate_distance_to_user(self, attraction: Dict[str, Any], user_location) -> Optional[float]:
        """Calculate distance between attraction and user location"""
        if not user_location or 'location' not in attraction:
            return None
            
        attraction_location = attraction['location']
        if 'lat' not in attraction_location or 'lng' not in attraction_location:
            return None
            
        import math
        R = 6371  # Earth radius in kilometers

        user_lat = user_location.lat
        user_lng = user_location.lng
            
        lat1 = math.radians(user_lat)
        lat2 = math.radians(attraction_location['lat'])
        delta_lat = math.radians(attraction_location['lat'] - user_lat)
        delta_lng = math.radians(attraction_location['lng'] - user_lng)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1) * math.cos(lat2) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c