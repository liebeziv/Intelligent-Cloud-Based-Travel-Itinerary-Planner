"""
Recommended System Base Class Definition
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseRecommender(ABC):
    """Recommended System Base Abstract Class"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.is_trained = False
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def recommend(self, user_id: str, **kwargs) -> List[Tuple[str, float]]:
        """
        Generate recommendations
        
        Args:
            user_id: User ID
            **kwargs: Other parameters

        Returns:
            List[Tuple[str, float]]: (attraction_id, score) list
        """
        pass
    
    def get_name(self) -> str:
        """Return the name of the recommender"""
        return self.name