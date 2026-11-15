# TITAN AI Operations Handbook

## Start
1. `cp .env.example .env` and set unique `API_KEY` and `POSTGRES_PASSWORD` values.
2. `docker compose up --build -d`
3. `docker compose exec ollama ollama pull llama3.2:3b`
4. `docker compose ps` and `curl http://localhost:8000/ready`.

## Backups
`docker compose exec -T postgres pg_dump -U titan titan > titan-backup.sql`

## Restore (destructive, test in a disposable environment first)
`cat titan-backup.sql | docker compose exec -T postgres psql -U titan titan`

## Troubleshooting
`docker compose logs --tail=200 api worker postgres ollama`

## Security
Never commit `.env`, private datasets, database dumps, or provider tokens. This stack binds the API and console to localhost by default. A shared browser API key is not suitable for Internet-facing deployments. Use an identity provider, TLS ingress, fine-grained authorization, migration tooling, and independent security review before public deployment.

## Jobs
Queue: `POST /api/v1/jobs`; inspect `GET /api/v1/jobs/{id}`; cancel queued jobs with `POST /api/v1/jobs/{id}/cancel`; retry failed jobs (maximum three attempts) with `POST /api/v1/jobs/{id}/retry`. Cancellation does not interrupt running jobs.
