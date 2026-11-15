# TITAN AI engineering release: verified scope and remaining gaps

This is a developer-oriented platform, NOT a production-certified enterprise service.

## Added in this release
- Scoped API keys with admin/operator/viewer access and revocation. Bootstrap key remains a superuser credential.
- Real asynchronous classical ML training for labeled text classification (TF-IDF + logistic regression), with holdout accuracy and serialized artifact.
- Background worker training jobs, artifacts on a shared persistent volume, operational counters in Prometheus text format.
- Frontend screens for training and scoped keys.
- Basic Kubernetes deployment example and observability starter.

## Not delivered or not verified
- LLM fine-tuning with LoRA/QLoRA; no GPU training scheduler or multi-GPU orchestration.
- OIDC, MFA, tenant isolation, per-resource policies, rate limiting, secret vault, automated key rotation.
- Multi-node distributed training, robust idempotency, lease-based job recovery and exactly-once semantics.
- Full MLflow experiment registry, automated deployment promotion, model rollback.
- Kubernetes cluster deployment, real GPU scheduling, vLLM routing, load/chaos/penetration testing.
- TLS termination and production infrastructure hardening, production backup restore drills.

## Important security constraints
- Do not expose the demo directly to the internet. Use HTTPS reverse proxy and private network.
- Treat the bootstrap API_KEY as a privileged secret. Generated API keys are returned only once; their hashes are stored.
- The admin API has no organization isolation. SQLite is only for local single-process development.
- Exported `.joblib` models are pickle-based; NEVER load artifacts from untrusted sources.
- Metrics endpoint is authenticated, so configure a dedicated read-only scraping credential.

## Training dataset format
Create a dataset via POST `/api/v1/datasets` with at least four `samples`, each containing `prompt` and `expected_contains`. For training, `expected_contains` is interpreted as the classification label. Provide multiple samples per class; train/test splitting may fail on tiny or unbalanced data. Use POST `/api/v1/training` with `name` and `dataset_id`, then GET `/api/v1/training` to check status and GET `/api/v1/training/{id}/artifact` to download. This trains a *classical classifier*, not a language model.
