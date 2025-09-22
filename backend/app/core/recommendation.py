from typing import List, Dict, Any, Tuple
import random
import logging

logger = logging.getLogger(__name__)

class HybridRecommender:
    def __init__(self):
        self._attractions = []
        self._initialized = False

    async def load_data(self, attractions: List[Dict[str, Any]]):
        """Load attractions data"""
        self._attractions = attractions
        self._initialized = True
        logger.info(f"HybridRecommender loaded {len(attractions)} attractions")

    async def recommend(
        self, 
        user_id: str,
        preferences: Dict[str, Any],
        current_location: Dict[str, Any] = None,
        exclude_visited: List[str] = None,
        top_k: int = 6,
        **kwargs
    ) -> List[Tuple[str, float]]:
        """Generate recommendations"""
        if not self._initialized:
            logger.warning("HybridRecommender not initialized")
            return []

        # Filter out visited attractions
        available_attractions = [
            a for a in self._attractions 
            if str(a['id']) not in (exclude_visited or [])
        ]

        # If no available attractions, return empty list
        if not available_attractions:
            logger.warning("No available attractions after filtering")
            return []

        # Match by categories
        activity_types = preferences.get('activity_types', [])
        matched_attractions = []
        
        for attraction in available_attractions:
            attraction_categories = set(attraction.get('categories', []))
            if not activity_types or attraction_categories & set(activity_types):
                # Calculate a more sophisticated matching score
                base_score = self._calculate_base_score(attraction, preferences)
                matched_attractions.append((str(attraction['id']), base_score))

        # Sort and return top k results
        matched_attractions.sort(key=lambda x: x[1], reverse=True)
        result = matched_attractions[:top_k]
        
        logger.info(f"Generated {len(result)} recommendations from {len(available_attractions)} available attractions")
        return result
    
    def _calculate_base_score(self, attraction: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """Calculate base score for an attraction"""
        score = 0.0
        
        # Category matching (40%)
        attraction_categories = set(attraction.get('categories', []))
        activity_types = preferences.get('activity_types', [])
        if activity_types:
            category_overlap = len(attraction_categories & set(activity_types))
            score += 0.4 * min(category_overlap / len(activity_types), 1.0)
        
        # Rating influence (30%)
        rating = attraction.get('rating', {}).get('average', 3.0)
        score += 0.3 * (rating / 5.0)
        
        # Popularity influence (20%)
        review_count = attraction.get('review_count', 0)
        popularity_score = min(review_count / 1000, 1.0)
        score += 0.2 * popularity_score
        
        # Add some randomness (10%)
        score += 0.1 * random.uniform(0, 1)
        
        return min(score, 1.0)