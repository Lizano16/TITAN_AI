# Delivery roadmap

- **Phase 1 (implemented):** model registry, Ollama gateway, single-step agents, runs, audit, dashboard, local Docker Compose, API tests, CI.
- **Phase 2:** OIDC, organizations, RBAC, Alembic migrations, pagination, rate limiting, hardened gateway.
- **Phase 3:** durable inference queues, workers, retry/backoff, cancellation, distributed tracing.
- **Phase 4:** multi-provider serving (vLLM, TGI), routing, streaming, batch jobs, evaluation harness.
- **Phase 5:** experiment tracking, fine-tuning pipelines, dataset and artifact versioning, GPU scheduling.
- **Phase 6:** Kubernetes deployment, autoscaling, billing/quotas, disaster recovery, penetration testing, benchmark publication.

Definition of done for each phase: automated tests, documented API, repeatable deployment, performance measurements, threat review, and real integration evidence.
