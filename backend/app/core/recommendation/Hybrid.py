from typing import List, Dict, Any, Tuple
import random
import logging
import math

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
        """Generate recommendations with distance filtering"""
        if not self._initialized:
            logger.warning("HybridRecommender not initialized")
            return []

        # Filter out visited attractions
        available_attractions = [
            a for a in self._attractions 
            if str(a['id']) not in (exclude_visited or [])
        ]

        if not available_attractions:
            logger.warning("No available attractions after filtering")
            return []

        # Apply distance filter (default 50km if not specified)
        max_distance = preferences.get('max_travel_distance', 50)
        if current_location and max_distance:
            available_attractions = self._filter_by_distance(
                available_attractions, current_location, max_distance
            )
            logger.info(f"After distance filtering ({max_distance}km): {len(available_attractions)} attractions")

        if not available_attractions:
            logger.warning(f"No attractions found within {max_distance}km of destination")
            return []

        # Calculate scores for all attractions within distance
        matched_attractions = []
        
        for attraction in available_attractions:
            base_score = self._calculate_base_score(attraction, preferences, current_location)
            if base_score > 0.2:  # Lower threshold for more variety
                matched_attractions.append((str(attraction['id']), base_score))

        # Sort and return top k results
        matched_attractions.sort(key=lambda x: x[1], reverse=True)
        result = matched_attractions[:top_k]
        
        logger.info(f"Generated {len(result)} recommendations from {len(available_attractions)} available attractions")
        return result
    
    def _filter_by_distance(self, attractions: List[Dict[str, Any]], user_location: Dict[str, Any], max_distance: float) -> List[Dict[str, Any]]:
        """Filter attractions by distance from user location"""
        filtered = []
        
        for attraction in attractions:
            distance = self._calculate_distance(attraction, user_location)
            if distance is not None and distance <= max_distance:
                # Store distance in attraction for later use
                attraction['_calculated_distance'] = distance
                filtered.append(attraction)
        
        return filtered
    
    def _calculate_base_score(self, attraction: Dict[str, Any], preferences: Dict[str, Any], user_location: Dict[str, Any] = None) -> float:
        """Calculate base score for an attraction"""
        score = 0.15  # Base score for all attractions
        
        # Category matching (30%)
        attraction_categories = set(attraction.get('categories', []))
        activity_types = preferences.get('activity_types', [])
        if activity_types:
            category_overlap = len(attraction_categories & set(activity_types))
            if category_overlap > 0:
                score += 0.30 * min(category_overlap / len(activity_types), 1.0)
            else:
                score += 0.08  # Small bonus for non-matching but potentially interesting
        else:
            score += 0.30
        
        # Rating influence (25%)
        rating = attraction.get('rating', {}).get('average', 3.0)
        score += 0.25 * (rating / 5.0)
        
        # Popularity influence (15%)
        review_count = attraction.get('review_count', 0)
        popularity_score = min(review_count / 1000, 1.0)
        score += 0.15 * popularity_score
        
        # Distance bonus (15%) - closer attractions get higher scores
        if user_location and '_calculated_distance' in attraction:
            distance = attraction['_calculated_distance']
            max_distance = preferences.get('max_travel_distance', 50)
            # Closer attractions get bonus points
            distance_score = max(0, 1 - (distance / max_distance))
            score += 0.15 * distance_score
        
        # Random factor for variety (15%)
        score += 0.15 * random.uniform(0, 1)
        
        return min(score, 1.0)

    def _calculate_distance(self, attraction: Dict[str, Any], user_location: Dict[str, Any]) -> float:
        """Calculate distance between attraction and user location"""
        if not user_location or 'location' not in attraction:
            return None
            
        attraction_location = attraction['location']
        if 'lat' not in attraction_location or 'lng' not in attraction_location:
            return None
            
        R = 6371  # Earth radius in kilometers

        lat1 = math.radians(user_location['lat'])
        lat2 = math.radians(attraction_location['lat'])
        delta_lat = math.radians(attraction_location['lat'] - user_location['lat'])
        delta_lng = math.radians(attraction_location['lng'] - user_location['lng'])
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1) * math.cos(lat2) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c