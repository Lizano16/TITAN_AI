# Security boundaries

- All `/api/v1/*` endpoints require `X-API-Key`; requests fail closed if API_KEY is absent.
- The key is shared across users: **this is not multi-tenant RBAC**. Never expose it in a public frontend deployment.
- Browser session storage is not suitable for long-lived production credentials.
- Keep the API bound to loopback for local demonstrations. Use HTTPS and an identity-aware gateway for remote access.
- Change default database credentials. Use a secret manager for real deployment.
- Ollama must remain on a private network; untrusted prompts must not execute shell commands.
- No security certification, penetration test, or isolation guarantee is claimed.
