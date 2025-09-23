def test_cors_preflight_root(client):
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    r = client.options("/", headers=headers)
    assert r.status_code in (200, 204)
    assert r.headers.get("access-control-allow-origin") in ("http://localhost:5173", "*")
    assert "access-control-allow-methods" in r.headers
