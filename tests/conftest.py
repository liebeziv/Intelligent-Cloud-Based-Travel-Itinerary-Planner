import os
import sys
import types
import pathlib

HERE = pathlib.Path(__file__).resolve()
BACKEND_ROOT = HERE.parents[1]
APP_DIR = BACKEND_ROOT / "app"
for p in (str(BACKEND_ROOT), str(APP_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

LEGACY_MOD = "app.core.recommendation.hybrid"
if LEGACY_MOD not in sys.modules:
    shim = types.ModuleType(LEGACY_MOD)

    class HybridRecommender:
        def __init__(self, *args, **kwargs):
            pass
        async def load_data(self, *args, **kwargs):
            return True
        async def initialize(self, *args, **kwargs):
            return True
        def recommend(self, *args, **kwargs):
            return []

    shim.HybridRecommender = HybridRecommender
    sys.modules[LEGACY_MOD] = shim

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ENVIRONMENT", "production")

import pytest
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from app.main import app

@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)

HAS_RECO = any(
    isinstance(r, APIRoute) and str(r.path).startswith("/api/recommendations")
    for r in app.router.routes
)
