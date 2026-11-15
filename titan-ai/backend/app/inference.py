import httpx
from .config import settings

async def generate(model_id: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{settings.ollama_url.rstrip('/')}/api/generate", json={"model": model_id, "prompt": prompt, "stream": False})
        response.raise_for_status()
        payload = response.json()
        return payload["response"]
