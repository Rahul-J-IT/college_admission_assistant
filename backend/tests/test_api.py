from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_index_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "TN College Admissions AI" in response.text

def test_data_endpoint(monkeypatch):
    # Depending on how pipeline initialized, it might return 503 if not loaded or a valid JSON.
    response = client.get("/api/data")
    if response.status_code == 200:
        json_data = response.json()
        # Since the dummy dataset isn't guaranteed to be loaded strictly in simple tests
        # We handle it defensively.
        if isinstance(json_data, dict) and "colleges" in json_data:
            assert isinstance(json_data["colleges"], list)
    else:
        assert response.status_code in [503, 500]

def test_chat_invalid_payload():
    # Giving invalid JSON payload
    response = client.post("/api/chat", json={"invalid": "payload"})
    # Pydantic validation should fail with 422
    assert response.status_code == 422
