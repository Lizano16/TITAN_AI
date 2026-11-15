import time
import secrets
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Security, Response
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .config import settings
from .db import Base, engine, get_db
from .models import ModelRegistry, InferenceRun, Agent, AuditEvent, Evaluation, Dataset, BackgroundJob
from .schemas import ModelCreate, InferenceRequest, AgentCreate, AgentRunRequest, EvaluationCreate, DatasetCreate
from .inference import generate
from .advanced import router as advanced_router
from .knowledge import router as knowledge_router
from .orchestration import router as orchestration_router
from .benchmark import router as benchmark_router
from .security import principal, require_role

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, version="0.5.0", lifespan=lifespan)
app.include_router(advanced_router)
app.include_router(knowledge_router)
app.include_router(orchestration_router)
app.include_router(benchmark_router)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(',')], allow_methods=["GET","POST"], allow_headers=["Content-Type","X-API-Key"])
header = APIKeyHeader(name="X-API-Key", auto_error=False)

def authenticate(user=Depends(principal)):
    return user

def audit(db: Session, action: str, resource: str, details: dict):
    db.add(AuditEvent(action=action, resource=resource, details=details))

@app.get("/health")
def health(): return {"status": "ok", "service": "titan-api"}

@app.get("/api/v1/overview", dependencies=[Depends(authenticate)])
def overview(db: Session = Depends(get_db)):
    return {"models": db.scalar(select(func.count()).select_from(ModelRegistry)), "agents": db.scalar(select(func.count()).select_from(Agent)), "inference_runs": db.scalar(select(func.count()).select_from(InferenceRun)), "failed_runs": db.scalar(select(func.count()).select_from(InferenceRun).where(InferenceRun.status == "failed")), "evaluations": db.scalar(select(func.count()).select_from(Evaluation)), "datasets": db.scalar(select(func.count()).select_from(Dataset))}

@app.get("/api/v1/models", dependencies=[Depends(authenticate)])
def models(db: Session = Depends(get_db)):
    return [{"id": m.id, "name": m.name, "provider": m.provider, "model_id": m.model_id, "description": m.description} for m in db.scalars(select(ModelRegistry).order_by(ModelRegistry.id.desc()))]

@app.post("/api/v1/models", status_code=201, dependencies=[Depends(require_role("operator"))])
def add_model(body: ModelCreate, db: Session = Depends(get_db)):
    if db.scalar(select(ModelRegistry).where(ModelRegistry.name == body.name)):
        raise HTTPException(409, "Model name already exists")
    model = ModelRegistry(**body.model_dump()); db.add(model)
    audit(db, "model.created", body.name, {"provider": body.provider})
    db.commit(); db.refresh(model)
    return {"id": model.id, "name": model.name}

@app.post("/api/v1/inference", dependencies=[Depends(require_role("operator"))])
async def inference(body: InferenceRequest, db: Session = Depends(get_db)):
    model = db.scalar(select(ModelRegistry).where(ModelRegistry.name == body.model_name))
    if not model: raise HTTPException(404, "Model not registered")
    run = InferenceRun(model_name=model.name, prompt=body.prompt)
    db.add(run); db.commit(); db.refresh(run)
    start = time.perf_counter()
    try:
        run.output = await generate(model.model_id, body.prompt)
        run.status = "completed"
    except Exception as exc:
        run.status = "failed"
        run.error = type(exc).__name__
    run.latency_ms = round((time.perf_counter()-start)*1000, 2)
    audit(db, "inference.finished", str(run.id), {"status": run.status})
    db.commit()
    if run.status == "failed": raise HTTPException(502, "Model provider unavailable or inference failed")
    return {"run_id": run.id, "model": model.name, "output": run.output, "latency_ms": run.latency_ms}

@app.get("/api/v1/runs", dependencies=[Depends(authenticate)])
def runs(db: Session = Depends(get_db)):
    return [{"id": r.id, "model": r.model_name, "status": r.status, "latency_ms": r.latency_ms, "created_at": r.created_at.isoformat()} for r in db.scalars(select(InferenceRun).order_by(InferenceRun.id.desc()).limit(100))]

@app.post("/api/v1/agents", status_code=201, dependencies=[Depends(require_role("operator"))])
def add_agent(body: AgentCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Agent).where(Agent.name == body.name)): raise HTTPException(409, "Agent exists")
    if not db.scalar(select(ModelRegistry).where(ModelRegistry.name == body.model_name)): raise HTTPException(404, "Model not registered")
    agent = Agent(**body.model_dump()); db.add(agent)
    audit(db, "agent.created", body.name, {})
    db.commit(); db.refresh(agent)
    return {"id": agent.id, "name": agent.name}

@app.get("/api/v1/agents", dependencies=[Depends(authenticate)])
def agents(db: Session = Depends(get_db)):
    return [{"id": a.id, "name": a.name, "model_name": a.model_name} for a in db.scalars(select(Agent).order_by(Agent.id.desc()))]

@app.post("/api/v1/agents/{agent_id}/run", dependencies=[Depends(require_role("operator"))])
async def run_agent(agent_id: int, body: AgentRunRequest, db: Session = Depends(get_db)):
    agent = db.get(Agent, agent_id)
    if not agent: raise HTTPException(404, "Agent not found")
    return await inference(InferenceRequest(model_name=agent.model_name, prompt=f"System instructions: {agent.instructions}\n\nUser task: {body.task}"), db)

@app.get("/api/v1/audit", dependencies=[Depends(require_role("admin"))])
def audit_log(db: Session = Depends(get_db)):
    return [{"action": e.action, "resource": e.resource, "details": e.details, "created_at": e.created_at.isoformat()} for e in db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(100))]

@app.get("/api/v1/datasets", dependencies=[Depends(authenticate)])
def list_datasets(db: Session = Depends(get_db)):
    return [{"id": x.id, "name": x.name, "description": x.description, "sample_count": len(x.samples)} for x in db.scalars(select(Dataset).order_by(Dataset.id.desc()).limit(100))]

@app.post("/api/v1/datasets", status_code=201, dependencies=[Depends(require_role("operator"))])
def create_dataset(body: DatasetCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Dataset).where(Dataset.name == body.name)):
        raise HTTPException(409, "Dataset name already exists")
    item = Dataset(name=body.name, description=body.description, samples=[x.model_dump() for x in body.samples])
    db.add(item)
    audit(db, "dataset.created", body.name, {"samples": len(body.samples)})
    db.commit(); db.refresh(item)
    return {"id": item.id, "name": item.name, "sample_count": len(item.samples)}

@app.get("/api/v1/evaluations", dependencies=[Depends(authenticate)])
def list_evaluations(db: Session = Depends(get_db)):
    return [{"id": x.id, "title": x.title, "model_name": x.model_name, "status": x.status, "score": x.score, "results": x.results, "created_at": x.created_at.isoformat()} for x in db.scalars(select(Evaluation).order_by(Evaluation.id.desc()).limit(100))]

@app.post("/api/v1/evaluations", status_code=201, dependencies=[Depends(require_role("operator"))])
async def evaluate(body: EvaluationCreate, db: Session = Depends(get_db)):
    model = db.scalar(select(ModelRegistry).where(ModelRegistry.name == body.model_name))
    if not model: raise HTTPException(404, "Model not registered")
    item = Evaluation(model_name=body.model_name, title=body.title, cases=[x.model_dump() for x in body.cases], status="running")
    db.add(item); db.commit(); db.refresh(item)
    results = []
    for case in body.cases:
        try:
            output = await generate(model.model_id, case.prompt)
            passed = case.expected_contains.casefold() in output.casefold()
            results.append({"prompt": case.prompt, "expected_contains": case.expected_contains, "output": output[:4000], "passed": passed})
        except Exception as exc:
            results.append({"prompt": case.prompt, "expected_contains": case.expected_contains, "error": type(exc).__name__, "passed": False})
    item.results = results
    item.score = round(sum(x["passed"] for x in results) / len(results) * 100, 2)
    item.status = "completed" if all("error" not in x for x in results) else "partial_failure"
    audit(db, "evaluation.finished", str(item.id), {"score": item.score, "status": item.status})
    db.commit()
    return {"id": item.id, "score": item.score, "status": item.status, "results": results}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(select(func.count()).select_from(ModelRegistry)).scalar()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(503, "Database not ready")

@app.post("/api/v1/jobs", status_code=202, dependencies=[Depends(require_role("operator"))])
def submit_job(body: InferenceRequest, db: Session = Depends(get_db)):
    if not db.scalar(select(ModelRegistry).where(ModelRegistry.name == body.model_name)):
        raise HTTPException(404, "Model not registered")
    job = BackgroundJob(kind="inference", payload=body.model_dump())
    db.add(job)
    audit(db, "job.submitted", body.model_name, {})
    db.commit()
    db.refresh(job)
    return {"id": job.id, "status": job.status}

@app.get("/api/v1/jobs", dependencies=[Depends(authenticate)])
def list_jobs(db: Session = Depends(get_db)):
    return [{"id": j.id, "kind": j.kind, "status": j.status, "attempts": j.attempts, "error": j.error, "created_at": j.created_at.isoformat()} for j in db.scalars(select(BackgroundJob).order_by(BackgroundJob.id.desc()).limit(100))]

@app.get("/api/v1/jobs/{job_id}", dependencies=[Depends(authenticate)])
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(BackgroundJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {"id": job.id, "kind": job.kind, "status": job.status, "result": job.result, "attempts": job.attempts, "error": job.error}


@app.post("/api/v1/jobs/{job_id}/cancel", dependencies=[Depends(require_role("operator"))])
def cancel_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(BackgroundJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.status != "queued":
        raise HTTPException(409, "Only queued jobs can be cancelled")
    job.status = "cancelled"
    audit(db, "job.cancelled", str(job.id), {})
    db.commit()
    return {"id": job.id, "status": job.status}

@app.post("/api/v1/jobs/{job_id}/retry", dependencies=[Depends(require_role("operator"))])
def retry_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(BackgroundJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.status != "failed":
        raise HTTPException(409, "Only failed jobs can be retried")
    if job.attempts >= 3:
        raise HTTPException(409, "Maximum attempts reached")
    job.status = "queued"
    job.error = ""
    audit(db, "job.retried", str(job.id), {})
    db.commit()
    return {"id": job.id, "status": job.status}

@app.get("/api/v1/metrics", dependencies=[Depends(authenticate)])
def metrics(db: Session = Depends(get_db)):
    statuses = db.execute(select(BackgroundJob.status, func.count()).group_by(BackgroundJob.status)).all()
    return {
        "jobs_by_status": {status: count for status, count in statuses},
        "mean_inference_latency_ms": round(db.scalar(select(func.avg(InferenceRun.latency_ms)).where(InferenceRun.status == "completed")) or 0, 2),
        "models": db.scalar(select(func.count()).select_from(ModelRegistry)),
        "datasets": db.scalar(select(func.count()).select_from(Dataset)),
    }

@app.get("/api/v1/datasets/{dataset_id}/export", dependencies=[Depends(authenticate)])
def export_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(404, "Dataset not found")
    return {"name": dataset.name, "description": dataset.description, "samples": dataset.samples}
