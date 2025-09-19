"""
Hybrid Recommender System Implementation
"""

from typing import List, Dict, Any, Tuple, Optional
import asyncio
import math
from datetime import datetime
from .base import BaseRecommender
from .content_based import ContentBasedRecommender

class HybridRecommender(BaseRecommender):
    """Hybrid Recommender System"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Initialize individual recommenders
        self.content_recommender = ContentBasedRecommender()

        # Weight configuration
        self.weights = {
            'content': 0.5,      # Content-based
            'location': 0.3,     # Location-based
            'popularity': 0.1,   # Popularity-based
            'real_time': 0.1     # Real-time factors
        }

        # Update weights
        if config and 'weights' in config:
            self.weights.update(config['weights'])
    
    async def load_data(self, attractions: List[Dict[str, Any]]):
        """Load all necessary data"""
        await self.content_recommender.load_attractions(attractions)
        self.attractions_data = attractions
        self.is_trained = True
    
    async def recommend(self, user_id: str, **kwargs) -> List[Tuple[str, float]]:
        """Hybrid recommendation"""
        if not self.is_trained:
            return []
        
        recommendations = {}
        top_k = kwargs.get('top_k', 10)

        # Content-based recommendations
        content_recs = await self.content_recommender.recommend(user_id, **kwargs)
        for attraction_id, score in content_recs:
            recommendations[attraction_id] = recommendations.get(attraction_id, 0) + \
                                           score * self.weights['content']
        
        # Location-based recommendations
        location_scores = await self._calculate_location_scores(
            kwargs.get('current_location'), 
            kwargs.get('preferences', {})
        )
        for attraction_id, score in location_scores.items():
            recommendations[attraction_id] = recommendations.get(attraction_id, 0) + \
                                           score * self.weights['location']

        # Popularity-based recommendations
        popularity_scores = self._calculate_popularity_scores()
        for attraction_id, score in popularity_scores.items():
            recommendations[attraction_id] = recommendations.get(attraction_id, 0) + \
                                           score * self.weights['popularity']

        # Real-time factors adjustment
        real_time_scores = await self._calculate_real_time_scores(kwargs.get('weather'))
        for attraction_id, score in real_time_scores.items():
            if attraction_id in recommendations:
                recommendations[attraction_id] *= score  # Multiply adjustment

        # Sort and return top-k recommendations
        sorted_recommendations = sorted(
            recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        return sorted_recommendations
    
    async def _calculate_location_scores(self, user_location: Optional[Dict], preferences: Dict) -> Dict[str, float]:
       
        scores = {}
        
        if not user_location:
            # If no location information is available, give all attractions the same base score
            for attraction in self.attractions_data:
                scores[attraction.get('id', str(hash(attraction['name'])))] = 0.5
            return scores
        
        user_lat = user_location.get('lat')
        user_lng = user_location.get('lng')
        max_travel_distance = preferences.get('max_travel_distance', 500)  # 500km by default
        
        for attraction in self.attractions_data:
            attraction_id = attraction.get('id', str(hash(attraction['name'])))
            location = attraction.get('location', {})
            
            if 'lat' in location and 'lng' in location:
                distance = self._calculate_distance(
                    user_lat, user_lng,
                    location['lat'], location['lng']
                )

                # Distance-based scoring with exponential decay
                if distance <= max_travel_distance:
                    score = math.exp(-distance / 100)  # 100km is the characteristic distance
                    scores[attraction_id] = score
                else:
                    scores[attraction_id] = 0.1  # Give a small score if out of range
            else:
                scores[attraction_id] = 0.3  # Give a medium score if no location information
        
        return scores
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        "Calculate the distance between two points (km) - using Haversine's formula"
        R = 6371  # Earth radius (km)

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng/2) * math.sin(delta_lng/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _calculate_popularity_scores(self) -> Dict[str, float]:
        "Calculating a heat-based score"
        scores = {}
        
        # Extract all ratings
        ratings = []
        for attraction in self.attractions_data:
            rating = attraction.get('rating', {})
            if isinstance(rating, dict):
                avg_rating = rating.get('average', 3.0)
                count = rating.get('count', 1)
            else:
                avg_rating = float(rating) if rating else 3.0
                count = attraction.get('review_count', 1)
            
            ratings.append((avg_rating, count))
        
        # Normalize ratings
        max_count = max([count for _, count in ratings]) if ratings else 1
        
        for i, attraction in enumerate(self.attractions_data):
            attraction_id = attraction.get('id', str(hash(attraction['name'])))
            avg_rating, count = ratings[i]
            
            # Combine ratings and review counts
            popularity_score = (avg_rating / 5.0) * 0.7 + (count / max_count) * 0.3
            scores[attraction_id] = min(popularity_score, 1.0)
        
        return scores
    
    async def _calculate_real_time_scores(self, weather_data: Optional[Dict]) -> Dict[str, float]:
        "Calculate real-time factor scores"
        scores = {}
        current_season = self._get_current_season()
        
        for attraction in self.attractions_data:
            attraction_id = attraction.get('id', str(hash(attraction['name'])))
            score_multiplier = 1.0

            # Season suitability
            best_seasons = attraction.get('best_seasons', [])
            if best_seasons and current_season in best_seasons:
                score_multiplier *= 1.3
            elif best_seasons and current_season not in best_seasons:
                score_multiplier *= 0.8

            # Weather suitability
            if weather_data:
                weather_suitability = self._check_weather_suitability(attraction, weather_data)
                score_multiplier *= weather_suitability
            
            scores[attraction_id] = score_multiplier
        
        return scores
    
    def _get_current_season(self) -> str:
        "Get the current season (Southern Hemisphere)"
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'summer'
        elif month in [3, 4, 5]:
            return 'autumn'
        elif month in [6, 7, 8]:
            return 'winter'
        else:
            return 'spring'
    
    def _check_weather_suitability(self, attraction: Dict, weather: Dict) -> float:
        "Check weather suitability"
        base_score = 1.0

        # Indoor/Outdoor activity
        is_outdoor = attraction.get('is_outdoor', True)
        
        if weather.get('condition') == 'rainy' and is_outdoor:
            base_score *= 0.6
        elif weather.get('condition') == 'sunny':
            base_score *= 1.2 if is_outdoor else 1.0

        # Temperature suitability
        temp = weather.get('temperature', 15)
        if 10 <= temp <= 25:  # Suitable temperature
            base_score *= 1.1
        elif temp < 0 or temp > 35:  # Extreme temperature
            base_score *= 0.7

        return min(base_score, 1.5)  # Max 1.5x multiplier