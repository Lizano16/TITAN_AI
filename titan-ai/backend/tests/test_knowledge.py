from types import SimpleNamespace
from app.knowledge import retrieve

def test_retrieval_relevant_and_cited():
    docs = [SimpleNamespace(id=1, title="PostgreSQL", content="PostgreSQL database stores records and SQL queries"), SimpleNamespace(id=2, title="Kubernetes", content="Kubernetes schedules pods and containers across cluster nodes")]
    hits = retrieve("How does Kubernetes schedule pods?", docs, 2)
    assert hits[0]["id"] == 2
    assert hits[0]["score"] > 0

def test_retrieval_empty():
    assert retrieve("unknown", []) == []
