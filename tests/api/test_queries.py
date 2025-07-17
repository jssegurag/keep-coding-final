import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_create_query():
    payload = {
        "query": "¿Cuál es el demandante del expediente?",
        "n_results": 3
    }
    response = client.post("/api/v1/queries/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "response" in data
    assert "timestamp" in data 