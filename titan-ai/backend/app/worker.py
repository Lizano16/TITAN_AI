"""Single-consumer durable database worker. Start one replica per queue with SQLite.
PostgreSQL supports multiple replicas via SKIP LOCKED row claiming.
"""
import asyncio
import logging
import os
from sqlalchemy import select
from .db import Base, engine, SessionLocal
from .models import BackgroundJob, ModelRegistry
from .training import train
from .inference import generate

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("titan.worker")

async def process_one():
    with SessionLocal() as db:
        query = select(BackgroundJob).where(BackgroundJob.status == "queued").order_by(BackgroundJob.id).limit(1)
        if engine.dialect.name == "postgresql":
            query = query.with_for_update(skip_locked=True)
        job = db.scalar(query)
        if job is None:
            return False
        job.status = "running"
        job.attempts += 1
        db.commit()
        job_id = job.id
        payload = dict(job.payload)
    try:
        if job.kind == "training":
            with SessionLocal() as db:
                train(db, payload["training_id"])
                from .models import TrainingRun
                result = db.get(TrainingRun, payload["training_id"])
                if result.status != "completed":
                    raise ValueError(result.error or "Training failed")
                job = db.get(BackgroundJob, job_id)
                job.result = {"training_id": result.id, "metrics": result.metrics}
                job.status = "completed"
                db.commit()
            return True
        if job.kind == "workflow":
            from .orchestration import WorkflowRequest, execute_workflow
            with SessionLocal() as db:
                result = await execute_workflow(WorkflowRequest(**payload), db)
                item = db.get(BackgroundJob, job_id)
                item.result = result
                item.status = "completed"
                db.commit()
            return True
        if job.kind != "inference":
            raise ValueError("Unsupported job kind")
        with SessionLocal() as db:
            model = db.scalar(select(ModelRegistry).where(ModelRegistry.name == payload["model_name"]))
            if model is None:
                raise ValueError("Model was removed")
            model_id = model.model_id
        output = await generate(model_id, payload["prompt"])
        with SessionLocal() as db:
            job = db.get(BackgroundJob, job_id)
            job.result = {"output": output, "model": payload["model_name"]}
            job.status = "completed"
            db.commit()
    except Exception as exc:
        log.exception("Job %s failed", job_id)
        with SessionLocal() as db:
            job = db.get(BackgroundJob, job_id)
            job.status = "failed"
            job.error = type(exc).__name__
            db.commit()
    return True

async def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # Requeue interrupted jobs on startup; requests must be idempotent for retry safety.
        for job in db.scalars(select(BackgroundJob).where(BackgroundJob.status == "running")):
            job.status = "queued"
        db.commit()
    while True:
        if not await process_one():
            await asyncio.sleep(float(os.getenv("WORKER_POLL_SECONDS", "2")))

if __name__ == "__main__":
    asyncio.run(main())
