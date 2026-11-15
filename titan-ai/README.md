# TITAN AI | Plataforma de ingeniería de IA

**Versión de portafolio v0.7.2 (código de demostración, no producto comercial).**

TITAN AI es un proyecto técnico para demostrar integración de IA, desarrollo full-stack, APIs, bases de datos, trabajos asíncronos, agentes controlados y evaluación. El repositorio contiene código fuente y ejemplos **sin datos privados ni credenciales reales**.

## Capacidades implementadas

- **Backend:** FastAPI, SQLAlchemy y PostgreSQL.
- **Frontend:** React, TypeScript y Vite; consola de administración.
- **Inferencia:** registro de modelos, acceso a Ollama y registro de ejecuciones.
- **Agentes:** ejecución sencilla y flujos de herramientas permitidas, con trazas.
- **Procesamiento asíncrono:** cola de trabajos persistentes con worker independiente, seguimiento de estado, cancelación y reintentos.
- **Conocimiento:** ingesta de documentos, búsqueda TF-IDF con fuentes y síntesis opcional con Ollama.
- **Entrenamiento:** clasificadores de texto con TF-IDF + regresión logística (NO entrenamiento ni fine-tuning de un LLM).
- **Evaluación:** pruebas deterministas, métricas F1/exact match, recuperación y latencia.
- **Seguridad de la demo:** API keys por roles, revocación y auditoría. No es un esquema de identidad apto para desplegar públicamente.
- **Despliegue local:** Docker Compose y pruebas automatizadas de backend.

## Arquitectura

```text
Navegador (React + Vite) :8081
         |
         v
    FastAPI :8000 <-----> PostgreSQL
         |                     ^
         +-----> Ollama        |
         |                     |
         +-----> cola de trabajos -> Worker
                     |
                     v
                artefactos locales
```

## Ejecutar localmente (Windows / PowerShell)

Requisitos: **Docker Desktop** con motor Linux en funcionamiento.

```powershell
Copy-Item .env.example .env
# Abre .env y configura POSTGRES_PASSWORD y API_KEY con valores aleatorios y secretos.
docker compose up --build -d
docker compose ps
docker compose exec ollama ollama pull llama3.2:3b
```

Genera dos claves distintas con Python (`python -c "import secrets; print(secrets.token_urlsafe(32))"`). Para la contraseña PostgreSQL utiliza caracteres seguros para una URL (por ejemplo, la salida de `secrets.token_urlsafe`) y no reutilices claves.

- Panel: **http://localhost:8081**
- Swagger API: **http://localhost:8000/docs**
- En la consola introduce el valor local de `API_KEY`, pulsa **Connect**, registra el modelo `llama3.2:3b` y prueba una inferencia.

## Pruebas

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

El frontend se compila con `cd frontend && npm install && npm run build` (también se construye en Docker). **No se afirma aquí que el despliegue entero haya sido auditado para producción.**

## Publicar de forma segura en GitHub

- `.env` **no se incluye**. Solo `.env.example`, con valores vacíos.
- Los datos de PostgreSQL, modelos descargados y artefactos de ejecución quedan en volúmenes de Docker; no forman parte de este ZIP.
- Ejecuta `python scripts/check_publication.py` antes de publicar.
- Consulta [docs/GITHUB_PUBLICATION.md](docs/GITHUB_PUBLICATION.md) y [docs/SEGURIDAD_PUBLICACION.md](docs/SEGURIDAD_PUBLICACION.md).
- Antes de exponer un servidor fuera de localhost, rediseña autenticación, TLS, control de acceso, secretos y endurecimiento de la API.

## Limitaciones

No incluye fine-tuning de LLM, ejecución distribuida real entre varias máquinas GPU, Kubernetes en operación ni garantías de disponibilidad. Los manifiestos de Kubernetes son ejemplos, no una infraestructura probada. Los clasificadores entrenados son modelos tradicionales y los artefactos `joblib` solo deben abrirse cuando sean confiables.

## Documentación técnica

`docs/ARCHITECTURE.md` · `docs/PORTFOLIO_DEMO.md` · `docs/KNOWLEDGE_RAG.md` · `docs/SECURITY.md` · `docs/ENTERPRISE_GAP_ANALYSIS.md`
