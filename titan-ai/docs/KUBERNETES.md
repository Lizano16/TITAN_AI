# Kubernetes deployment starter (not production-ready)

The `infra/k8s` directory provides example API and worker deployments and a service. Before deploying, provision a PostgreSQL database, Ollama endpoint, persistent artifact volume and Kubernetes secret `titan-config` containing `DATABASE_URL`, `API_KEY`, `OLLAMA_URL`, `ARTIFACT_DIR`. Build and push the backend image and replace `REPLACE_WITH_BACKEND_IMAGE` in the manifest.

This starter is not a turnkey distributed platform. For training artifact persistence, mount a real ReadWriteMany persistent volume to `/artifacts` on API and workers. Add ingress TLS, autoscaling, pod disruption budgets, network policies, secret management, database migrations and operational monitoring. Do not use SQLite with multiple replicas.
