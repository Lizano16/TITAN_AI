import os
os.environ["API_KEY"] = "test-secret-key"
import os
os.environ["DATABASE_URL"] = "sqlite:///./titan_test.db"
from fastapi.testclient import TestClient
from app.main import app

def test_dataset_and_evaluation(monkeypatch):
    async def fake_generate(model_id, prompt):
        return "TITAN works"
    monkeypatch.setattr("app.main.generate", fake_generate)
    with TestClient(app, headers={"X-API-Key": "test-secret-key"}) as client:
        client.post("/api/v1/models", json={"name":"eval-local", "model_id":"test-model"})
        d = client.post("/api/v1/datasets", json={"name":"smoke-data", "samples":[{"prompt":"hello", "expected_contains":"TITAN"}]})
        assert d.status_code in (201,409)
        assert any(x["name"]=="smoke-data" for x in client.get("/api/v1/datasets").json())
        r = client.post("/api/v1/evaluations", json={"title":"smoke", "model_name":"eval-local", "cases":[{"prompt":"hello", "expected_contains":"titan"}]})
        assert r.status_code == 201
        assert r.json()["score"] == 100
        assert len(client.get("/api/v1/evaluations").json()) >= 1
