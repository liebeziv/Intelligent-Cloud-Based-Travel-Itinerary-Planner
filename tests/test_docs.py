def test_docs_available(client):
    # Swagger UI
    r = client.get("/docs")
    assert r.status_code == 200

    # ReDoc
    r = client.get("/redoc")
    assert r.status_code == 200

def test_openapi_schema(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "openapi" in data
    assert "paths" in data
    assert data["info"]["title"]
