"""
Content-based recommendation algorithm implementation
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple, Optional
import json
import asyncio
from .base import BaseRecommender

class ContentBasedRecommender(BaseRecommender):
    """Content-based recommender"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.attraction_features = None
        self.attractions_data = []
        self.feature_matrix = None
        
    async def load_attractions(self, attractions: List[Dict[str, Any]]):
        """Load attraction data"""
        self.attractions_data = attractions
        await self._prepare_features()
        
    async def _prepare_features(self):
        """Prepare attraction feature vectors"""
        if not self.attractions_data:
            return
            
        feature_texts = []
        for attraction in self.attractions_data:
            # Combine text features
            features = []
            
            # Add categories
            if 'categories' in attraction:
                features.extend(attraction['categories'])
            
            # Add feature tags
            if 'features' in attraction:
                for key, value in attraction['features'].items():
                    if isinstance(value, str):
                        features.append(f"{key}_{value}")
                    elif isinstance(value, list):
                        features.extend([f"{key}_{v}" for v in value])

            # Add description
            if 'description' in attraction:
                features.append(attraction['description'])

            # Add region information
            if 'region' in attraction:
                features.append(f"region_{attraction['region']}")
                
            feature_texts.append(' '.join(str(f) for f in features))

        # Vectorization
        self.feature_matrix = self.vectorizer.fit_transform(feature_texts)
        self.is_trained = True
        
    async def recommend(self, user_id: str, **kwargs) -> List[Tuple[str, float]]:
        """Content-based recommendation"""
        if not self.is_trained:
            return []
            
        user_preferences = kwargs.get('preferences', {})
        top_k = kwargs.get('top_k', 10)
        exclude_visited = kwargs.get('exclude_visited', [])

        # Build user preference vector
        user_features = self._build_user_vector(user_preferences)
        if user_features is None:
            return []

        # Compute similarity
        similarities = cosine_similarity(user_features, self.feature_matrix).flatten()

        # Sort and filter
        recommendations = []
        for i, similarity in enumerate(similarities):
            attraction = self.attractions_data[i]
            attraction_id = attraction.get('id', str(i))

            # Skip visited attractions
            if attraction_id in exclude_visited:
                continue

            # Apply other filters
            if self._passes_filters(attraction, user_preferences):
                recommendations.append((attraction_id, float(similarity)))

        # Sort by similarity
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def _build_user_vector(self, preferences: Dict[str, Any]) -> Optional[np.ndarray]:
        """Build user preference vector"""
        user_features = []
        
        # Activity type preferences
        if 'activity_types' in preferences:
            user_features.extend(preferences['activity_types'])

        # Travel style
        if 'travel_style' in preferences:
            user_features.append(f"style_{preferences['travel_style']}")

        # Difficulty preference
        if 'difficulty_preference' in preferences:
            user_features.append(f"difficulty_{preferences['difficulty_preference']}")

        # Season preference
        if 'season' in preferences:
            user_features.append(f"season_{preferences['season']}")
        
        if not user_features:
            return None
            
        user_text = ' '.join(user_features)
        try:
            return self.vectorizer.transform([user_text])
        except Exception:
            return None
    
    def _passes_filters(self, attraction: Dict[str, Any], preferences: Dict[str, Any]) -> bool:
        """Check if the attraction passes the user filter criteria"""

        # Budget filter
        if 'budget_range' in preferences:
            min_budget, max_budget = preferences['budget_range']
            attraction_price = attraction.get('price_level', 2)  # Default to medium price
            if not (min_budget <= attraction_price <= max_budget):
                return False

        # Difficulty filter
        if 'max_difficulty' in preferences:
            attraction_difficulty = attraction.get('difficulty_level', 1)
            if attraction_difficulty > preferences['max_difficulty']:
                return False
                
        return True