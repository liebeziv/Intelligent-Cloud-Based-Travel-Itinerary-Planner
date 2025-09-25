def test_upload_url_requires_auth(client):
    r = client.get("/api/upload-url", params={"filename": "a.png"})
    assert r.status_code in (401, 403)