# TITAN AI · Engineering demonstration

This is an **engineering portfolio reference implementation**, not an audited commercial service.

## Included demos

1. Register an Ollama model via `POST /api/v1/models`.
2. Ingest technical documents via `POST /api/v1/knowledge/documents`.
3. Run a **bounded multi-step agent** via `POST /api/v1/orchestration/workflows`:

```json
{"task":"Summarize our incident response policy","model_name":"local","steps":["retrieve","calculate","synthesize"],"expression":"(12+8)/4"}
```

4. Submit the same request to `/api/v1/orchestration/workflows/queue`, then poll `/api/v1/jobs/{id}`; the database-backed worker processes it independently.
5. Compare outputs using `/api/v1/benchmark/score`:

```json
{"k":3,"cases":[{"predicted":"service restored","reference":"service restored","latency_ms":120,"retrieved_ids":[1,2],"relevant_ids":[2]}]}
```

6. Train a TF-IDF + logistic regression classifier via the dataset/training APIs, inspect metrics, and export the model artifact. **This is not LLM fine-tuning.**
7. Run the automated backend tests with `cd backend && python -m pytest -q`.

## Architecture

`React UI → FastAPI → PostgreSQL → database job queue → worker → Ollama`.

Retrieval is lexical TF-IDF, not embedding-based. Workflow tools are explicitly allowlisted (retrieval, bounded arithmetic, synthesis), not arbitrary execution. Agent traces show step durations and evidence IDs. Benchmark metrics are exact match, token F1, retrieval recall@k and latency; they do not independently prove answer correctness or safety.

## Operational limitations

A single-worker SQLite development setup is not a fault-tolerant cluster. Use PostgreSQL for multiple workers. This reference implementation has no production-ready tenant isolation, OIDC, distributed GPU scheduling, LoRA/QLoRA or validated Kubernetes autoscaling. Do not expose it publicly without security review.
