"""Operational features: scoped API keys, offline training and metrics."""
import hashlib
import os
import secrets
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .db import get_db
from .models import AccessKey, TrainingRun, Dataset, BackgroundJob, InferenceRun
from .security import require_role

router = APIRouter(prefix="/api/v1")

class KeyRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    role: str = Field(pattern="^(viewer|operator|admin)$")

@router.post("/access-keys", status_code=201)
def create_key(body: KeyRequest, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    if db.scalar(select(AccessKey).where(AccessKey.name == body.name)):
        raise HTTPException(409, "Name exists")
    raw = "titan_" + secrets.token_urlsafe(36)
    record = AccessKey(name=body.name, role=body.role, key_hash=hashlib.sha256(raw.encode()).hexdigest())
    db.add(record); db.commit(); db.refresh(record)
    return {"id": record.id, "name": record.name, "role": record.role, "api_key": raw, "warning": "Save this key now. It will not be shown again."}

@router.get("/access-keys")
def list_keys(db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    return [{"id": k.id, "name": k.name, "role": k.role, "active": k.active} for k in db.scalars(select(AccessKey).order_by(AccessKey.id))]

@router.delete("/access-keys/{key_id}")
def revoke_key(key_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    key = db.get(AccessKey, key_id)
    if not key: raise HTTPException(404, "Not found")
    key.active = False; db.commit()
    return {"revoked": True}

class TrainRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    dataset_id: int = Field(gt=0)

@router.post("/training", status_code=202)
def submit_training(body: TrainRequest, db: Session = Depends(get_db), _=Depends(require_role("operator"))):
    dataset = db.get(Dataset, body.dataset_id)
    if not dataset: raise HTTPException(404, "Dataset not found")
    if len(dataset.samples) < 4: raise HTTPException(422, "At least four labeled samples required")
    if not all(isinstance(s.get("prompt"), str) and isinstance(s.get("expected_contains"), str) and s["prompt"] and s["expected_contains"] for s in dataset.samples):
        raise HTTPException(422, "Samples require prompt and response")
    run = TrainingRun(name=body.name, dataset_id=body.dataset_id)
    db.add(run); db.flush()
    db.add(BackgroundJob(kind="training", payload={"training_id": run.id}))
    db.commit()
    return {"id": run.id, "status": "queued"}

@router.get("/training")
def training(db: Session = Depends(get_db), _=Depends(require_role("viewer"))):
    return [{"id": r.id, "name": r.name, "dataset_id": r.dataset_id, "status": r.status, "metrics": r.metrics, "error": r.error} for r in db.scalars(select(TrainingRun).order_by(TrainingRun.id.desc()).limit(100))]

@router.get("/training/{run_id}/artifact")
def training_artifact(run_id: int, db: Session = Depends(get_db), _=Depends(require_role("operator"))):
    from fastapi.responses import FileResponse
    r = db.get(TrainingRun, run_id)
    if not r: raise HTTPException(404, "Not found")
    if r.status != "completed" or not r.artifact_path: raise HTTPException(409, "Training not completed")
    root = Path(os.getenv("ARTIFACT_DIR", "/tmp/titan-artifacts")).resolve()
    path = Path(r.artifact_path).resolve()
    if not path.is_relative_to(root) or not path.is_file(): raise HTTPException(404, "Artifact unavailable")
    return FileResponse(path, filename=f"titan-model-{run_id}.joblib")

@router.get("/metrics")
def metrics(db: Session = Depends(get_db), _=Depends(require_role("viewer"))):
    from fastapi.responses import PlainTextResponse
    lines = ["# TYPE titan_jobs_total gauge"]
    for status, count in db.execute(select(BackgroundJob.status, func.count()).group_by(BackgroundJob.status)):
        lines.append(f'titan_jobs_total{{status="{status}"}} {count}')
    lines.append("# TYPE titan_inference_total gauge")
    for status, count in db.execute(select(InferenceRun.status, func.count()).group_by(InferenceRun.status)):
        lines.append(f'titan_inference_total{{status="{status}"}} {count}')
    return PlainTextResponse("\n".join(lines)+"\n", media_type="text/plain; version=0.0.4")
