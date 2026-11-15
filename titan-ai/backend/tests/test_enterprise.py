import os
os.environ['API_KEY'] = 'test-secret-key'
os.environ['DATABASE_URL'] = 'sqlite:///./titan_test.db'
from fastapi.testclient import TestClient
from app.main import app

def test_access_keys_and_roles():
    with TestClient(app) as c:
        admin={'X-API-Key':'test-secret-key'}
        res=c.post('/api/v1/access-keys',headers=admin,json={'name':'test-viewer-key','role':'viewer'})
        assert res.status_code in (201,409)
        if res.status_code == 201:
            viewer={'X-API-Key':res.json()['api_key']}
            assert c.get('/api/v1/models',headers=viewer).status_code == 200
            assert c.post('/api/v1/models',headers=viewer,json={'name':'x-model','model_id':'x-model'}).status_code == 403
            assert c.get('/api/v1/access-keys',headers=viewer).status_code == 403
            assert c.delete(f"/api/v1/access-keys/{res.json()['id']}",headers=admin).status_code == 200
            assert c.get('/api/v1/models',headers=viewer).status_code == 401

def test_training_validation():
    with TestClient(app,headers={'X-API-Key':'test-secret-key'}) as c:
        assert c.post('/api/v1/training',json={'name':'my-run','dataset_id':999999}).status_code == 404
        assert c.get('/api/v1/training').status_code == 200
        assert c.get('/api/v1/metrics').status_code == 200
