import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

HAS_RECO = any(
    str(r.path).startswith("/api/recommendations")
    for r in app.router.routes
)
