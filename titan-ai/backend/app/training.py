"""Actual offline text classification training with holdout evaluation.
This is NOT LLM fine-tuning. No remote model or GPU required.
"""
import os
from pathlib import Path
from sqlalchemy.orm import Session
from .models import TrainingRun, Dataset

def train(db: Session, training_id: int):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import joblib
    run = db.get(TrainingRun, training_id)
    if run is None: raise ValueError("Training run not found")
    run.status = "running"; db.commit()
    try:
        dataset = db.get(Dataset, run.dataset_id)
        samples = dataset.samples
        x = [s["prompt"] for s in samples]
        y = [s["expected_contains"] for s in samples]
        if len(set(y)) < 2: raise ValueError("At least two distinct target labels required")
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)
        if len(set(y_train)) < 2: raise ValueError("Insufficient training samples per class")
        pipeline = make_pipeline(TfidfVectorizer(ngram_range=(1,2)), LogisticRegression(max_iter=500))
        pipeline.fit(x_train, y_train)
        accuracy = float(accuracy_score(y_test, pipeline.predict(x_test)))
        root = Path(os.getenv("ARTIFACT_DIR", "/tmp/titan-artifacts")).resolve()
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"training-{run.id}.joblib"
        joblib.dump(pipeline, path)
        run.metrics = {"holdout_accuracy": accuracy, "train_samples": len(x_train), "test_samples": len(x_test), "algorithm": "TF-IDF + LogisticRegression"}
        run.artifact_path = str(path)
        run.status = "completed"
    except Exception as exc:
        run.status = "failed"; run.error = str(exc)[:500]
    db.commit()
