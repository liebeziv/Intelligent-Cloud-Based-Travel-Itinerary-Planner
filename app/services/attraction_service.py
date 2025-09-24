"""Utility helpers for exposing attraction data via the API."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from app.data.sample_attractions import SAMPLE_NZ_ATTRACTIONS


class AttractionService:
    """Simple in-memory service backed by the sample attraction dataset."""

    def __init__(self, attractions: Optional[Iterable[Dict]] = None) -> None:
        self._attractions: List[Dict] = list(attractions or SAMPLE_NZ_ATTRACTIONS)

    def list_attractions(
        self,
        *,
        region: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Return attractions optionally filtered by region/category."""

        filtered: List[Dict] = []
        region_lower = region.lower() if region else None
        category_lower = category.lower() if category else None

        for attraction in self._attractions:
            if region_lower and attraction.get("region", "").lower() != region_lower:
                continue

            categories = attraction.get("categories", []) or []
            if category_lower and category_lower not in {c.lower() for c in categories}:
                continue

            filtered.append(self._normalise(attraction))

            if limit and len(filtered) >= limit:
                break

        if not filtered:
            # Still normalise the data so the response shape is consistent
            return [self._normalise(item) for item in self._attractions[: limit or None]]

        return filtered

    def get_attraction(self, attraction_id: str) -> Optional[Dict]:
        """Return a single attraction by id if it exists."""

        for attraction in self._attractions:
            if attraction.get("id") == attraction_id:
                return self._normalise(attraction)
        return None

    def _normalise(self, attraction: Dict) -> Dict:
        """Enrich raw dictionaries with friendly fields for clients."""

        rating = attraction.get("rating", {}) or {}
        average_rating = rating.get("average") if isinstance(rating, dict) else rating
        rating_count = rating.get("count") if isinstance(rating, dict) else None

        categories = attraction.get("categories") or []
        primary_category = categories[0] if categories else None

        price_range = attraction.get("price_range")
        if not price_range:
            price_level = attraction.get("features", {}).get("price_level")
            if isinstance(price_level, int):
                base = max(price_level * 40, 40)
                price_range = [base, base + 120]
            else:
                price_range = None

        return {
            **attraction,
            "category": primary_category,
            "rating": round(float(average_rating), 1) if average_rating else None,
            "rating_count": rating_count,
            "price_range": price_range,
        }


attraction_service = AttractionService()