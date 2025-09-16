# Recommended system core module initialisation

from .base import BaseRecommender
from .content_based import ContentBasedRecommender
from .hybrid import HybridRecommender

__all__ = [
    'BaseRecommender',
    'ContentBasedRecommender', 
    'HybridRecommender'
]