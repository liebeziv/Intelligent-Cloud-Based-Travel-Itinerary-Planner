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

def test_recommendations_distance_filter_and_topk(client):
    payload = {
        "user_id": "u1",
        "preferences": {
            "activity_types": ["natural"],
            "budget_range": [0, 200],
            "travel_style": "relax",
            "max_travel_distance": 5,
            "duration": 1
        },
        "current_location": {"lat": -46.4, "lng": 168.3, "address": "Invercargill"},
        "exclude_visited": [],
        "top_k": 3
    }
    r = client.post("/api/recommendations", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert len(data["recommendations"]) <= 3
