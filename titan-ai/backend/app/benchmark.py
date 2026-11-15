"""Offline, reproducible evaluation metrics for model and retrieval results."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from .security import require_role

router = APIRouter(prefix="/api/v1/benchmark", tags=["benchmark"])

class BenchmarkCase(BaseModel):
    predicted: str
    reference: str
    latency_ms: float = Field(ge=0)
    retrieved_ids: list[int] = Field(default_factory=list)
    relevant_ids: list[int] = Field(default_factory=list)

class BenchmarkRequest(BaseModel):
    cases: list[BenchmarkCase] = Field(min_length=1, max_length=1000)
    k: int = Field(default=3, ge=1, le=100)

def score(cases: list[BenchmarkCase], k: int):
    exact = 0; f1_sum = 0.; recall_sum = 0.; latency = []
    for case in cases:
        pred = case.predicted.casefold().split(); ref = case.reference.casefold().split()
        exact += int(" ".join(pred) == " ".join(ref))
        from collections import Counter
        overlap = sum((Counter(pred) & Counter(ref)).values())
        precision = overlap / len(pred) if pred else 0
        recall = overlap / len(ref) if ref else 0
        f1_sum += 2*precision*recall/(precision+recall) if precision+recall else 0
        relevant = set(case.relevant_ids)
        recall_sum += len(set(case.retrieved_ids[:k]) & relevant)/len(relevant) if relevant else 1
        latency.append(case.latency_ms)
    n = len(cases)
    latency.sort()
    return {"count": n, "exact_match": round(exact/n, 4), "token_f1": round(f1_sum/n, 4),
            "retrieval_recall_at_k": round(recall_sum/n, 4), "mean_latency_ms": round(sum(latency)/n, 2),
            "p95_latency_ms": latency[max(0, int(.95*(n-1)))], "k": k}

@router.post("/score")
def benchmark(body: BenchmarkRequest, _=Depends(require_role("operator"))):
    return score(body.cases, body.k)
