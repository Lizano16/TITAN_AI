# TITAN Knowledge: grounded retrieval

TITAN exposes an authenticated knowledge base with document ingestion, ranked retrieval, deletion and optional model-based synthesis.

- `POST /api/v1/knowledge/documents`: `{ "title": "...", "content": "..." }` (operator)
- `GET /api/v1/knowledge/documents`: list document metadata
- `DELETE /api/v1/knowledge/documents/{id}`: delete (operator)
- `POST /api/v1/knowledge/search`: `{ "question": "...", "top_k": 3 }`
- Add `"model_name": "<registered-model>"` to synthesize an answer using Ollama.

Every response includes ranked source IDs and excerpts. Without a model name, the endpoint is fully deterministic and requires no LLM. The baseline uses TF-IDF (word unigrams and bigrams), not embeddings. This is intentionally explicit so reviewers can compare lexical retrieval with future vector or hybrid search. There is no claim of verified citations in generated text; consumers should inspect the returned matches. Documents are trusted as data, not as instructions.

## Limitations

Corpus is re-vectorized per request; suitable for demos, not large document stores. No tenant isolation or file ingestion. LLM responses may hallucinate despite grounding prompts. Never upload confidential documents to a public demonstration instance.
