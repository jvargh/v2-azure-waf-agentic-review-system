"""(Relocated) Direct API test using FastAPI TestClient (no uvicorn)"""
from fastapi.testclient import TestClient
import json
from backend.server import app

client = TestClient(app)

def test_create_and_list():
    payload = {"name": "direct-assessment", "description": "created via TestClient"}
    r = client.post("/api/assessments", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    aid = data["id"]
    # list
    r2 = client.get("/api/assessments")
    assert r2.status_code == 200, r2.text
    items = r2.json()
    found = any(a["id"] == aid for a in items)
    assert found

if __name__ == "__main__":  # pragma: no cover
    test_create_and_list()
    print("✅ Direct API test passed")
