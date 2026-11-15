#!/usr/bin/env python3
"""Simple pre-publication check, deliberately conservative, not a complete secret scanner."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache"}
BAD_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "service-account.json"}
BAD_EXTENSIONS = {".pem", ".p12", ".pfx", ".key", ".sqlite", ".sqlite3", ".db", ".sql", ".dump", ".bak", ".log", ".joblib", ".pkl"}
PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(rb"\b(?:ghp_|gho_|ghu_|ghs_|ghr_|github_pat_)[A-Za-z0-9_]{20,}"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}"),
]

def should_skip(path: Path) -> bool:
    return bool(SKIP_DIRS.intersection(path.relative_to(ROOT).parts))

def main() -> int:
    problems = []
    checked = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        rel = path.relative_to(ROOT)
        checked += 1
        if path.name in BAD_NAMES or (path.name.startswith(".env.") and path.name != ".env.example") or path.suffix.lower() in BAD_EXTENSIONS:
            problems.append(f"Archivo privado: {rel}")
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            problems.append(f"No se pudo leer: {rel}: {exc}")
            continue
        for regex in PATTERNS:
            if regex.search(data):
                problems.append(f"Posible credencial en {rel}: {regex.pattern!r}")
    if problems:
        print("ERROR: Revisa antes de publicar:")
        print("\n".join(problems))
        return 1
    print(f"OK: {checked} archivos revisados, sin secretos reconocibles ni archivos privados prohibidos.")
    print("Advertencia: el chequeo no equivale a una auditoría de seguridad completa.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
