import os
os.environ['API_KEY'] = 'test-secret-key'
from fastapi.testclient import TestClient
from app.main import app

def test_job_queue_and_authentication():
    with TestClient(app) as client:
        assert client.get('/api/v1/jobs').status_code == 401
        headers = {'X-API-Key': 'test-secret-key'}
        client.post('/api/v1/models', json={'name':'job-test-model', 'model_id':'llama3.2:3b'}, headers=headers)
        response = client.post('/api/v1/jobs', json={'model_name':'job-test-model','prompt':'hello'}, headers=headers)
        assert response.status_code == 202
        job = client.get(f"/api/v1/jobs/{response.json()['id']}", headers=headers)
        assert job.status_code == 200
        assert job.json()['status'] == 'queued'
        assert client.get('/ready').status_code == 200
