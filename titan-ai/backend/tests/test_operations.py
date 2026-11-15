import os
os.environ["API_KEY"] = "test-secret-key"
from fastapi.testclient import TestClient
from app.main import app

H = {"X-API-Key": "test-secret-key"}

def test_operations_and_metrics():
    with TestClient(app) as client:
        assert client.get("/api/v1/metrics").status_code == 401
        assert client.get("/api/v1/metrics", headers=H).status_code == 200
        client.post("/api/v1/models", json={"name":"ops-test-model", "model_id":"llama3.2:3b"}, headers=H)
        created = client.post("/api/v1/jobs", json={"model_name":"ops-test-model", "prompt":"hello"}, headers=H)
        assert created.status_code == 202
        job_id = created.json()["id"]
        assert client.post(f"/api/v1/jobs/{job_id}/cancel", headers=H).json()["status"] == "cancelled"
        assert client.post(f"/api/v1/jobs/{job_id}/cancel", headers=H).status_code == 409
        assert client.post(f"/api/v1/jobs/{job_id}/retry", headers=H).status_code == 409
        assert client.post("/api/v1/jobs/999999/cancel", headers=H).status_code == 404
