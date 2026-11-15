"""API key roles. Bootstrap API_KEY is an administrator credential.
Persist only SHA256 digests of randomly generated API keys.
"""
import hashlib
import secrets
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import AccessKey

header = APIKeyHeader(name="X-API-Key", auto_error=False)
ROLES = {"viewer": 0, "operator": 1, "admin": 2}

def principal(key: str | None = Security(header), db: Session = Depends(get_db)):
    if not key:
        raise HTTPException(401, "Missing API key")
    if settings.api_key and secrets.compare_digest(key, settings.api_key):
        return {"name": "bootstrap", "role": "admin"}
    digest = hashlib.sha256(key.encode()).hexdigest()
    record = db.scalar(select(AccessKey).where(AccessKey.key_hash == digest, AccessKey.active.is_(True)))
    if not record:
        raise HTTPException(401, "Invalid API key")
    return {"name": record.name, "role": record.role}

def require_role(role):
    def check(user=Depends(principal)):
        if ROLES[user["role"]] < ROLES[role]:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return check
