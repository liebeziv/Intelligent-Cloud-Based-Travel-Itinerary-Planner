def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()

    assert data["status"] == "healthy"
    assert data["service"] == "travel-planner-api"

    for key in ("timestamp", "version", "environment", "components"):
        assert key in data

    comps = data["components"]
    assert isinstance(comps, dict)
    for k in ("auth", "s3utils", "sns_utils"):
        assert k in comps
