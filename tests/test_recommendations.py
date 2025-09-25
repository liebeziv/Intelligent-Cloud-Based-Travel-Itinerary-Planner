import pytest
from fastapi.routing import APIRoute
from app.main import app

HAS_RECO = any(
    isinstance(r, APIRoute) and str(r.path).startswith("/api/recommendations")
    for r in app.router.routes
)
pytestmark = pytest.mark.skipif(
    not HAS_RECO, reason="Recommendations API not registered in this build"
)

def test_recommendations_basic(client):
    payload = {
        "user_id": "test_user",
        "preferences": {
            "activity_types": ["natural", "scenic"],
            "budget_range": [100, 400],
            "travel_style": "adventure",
            "difficulty_preference": "medium",
            "max_travel_distance": 300,
            "group_size": 2,
            "duration": 3
        },
        "current_location": {
            "lat": -41.3,
            "lng": 174.8,
            "address": "Wellington, New Zealand"
        },
        "exclude_visited": [],
        "top_k": 5
    }
    r = client.post("/api/recommendations", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "recommendations" in data
    assert "total_count" in data
    assert "algorithm_used" in data
    assert isinstance(data["recommendations"], list)
    assert 0 <= len(data["recommendations"]) <= payload["top_k"]
    if data["recommendations"]:
        rec = data["recommendations"][0]
        for key in ["id", "name", "categories", "score", "confidence_score"]:
            assert key in rec
        assert 0.0 <= rec["score"] <= 1.0
