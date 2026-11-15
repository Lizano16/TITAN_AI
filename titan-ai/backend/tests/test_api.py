import os
os.environ["API_KEY"] = "test-secret-key"
import os
os.environ["DATABASE_URL"] = "sqlite:///./titan_test.db"
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app, headers={"X-API-Key": "test-secret-key"}) as client:
        assert client.get("/health").json()["status"] == "ok"

def test_model_lifecycle():
    with TestClient(app, headers={"X-API-Key": "test-secret-key"}) as client:
        response = client.post("/api/v1/models", json={"name": "test-local", "model_id": "llama3.2:3b"})
        assert response.status_code in (201, 409)
        assert any(x["name"] == "test-local" for x in client.get("/api/v1/models").json())
        assert client.post("/api/v1/inference", json={"model_name": "missing", "prompt": "hello"}).status_code == 404

def test_agent_validation():
    with TestClient(app, headers={"X-API-Key": "test-secret-key"}) as client:
        assert client.post("/api/v1/agents", json={"name":"xagent", "instructions":"Help", "model_name":"not-found"}).status_code == 404
