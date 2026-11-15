# Seguridad del repositorio público

Esta entrega solo incluye **código de ejemplo y de demostración**, no credenciales de usuarios ni datos privados. El archivo `.env.example` está intencionalmente vacío.

## Nunca publicar

- `.env` real, contraseñas de PostgreSQL, `API_KEY` u otros tokens.
- Archivos `.pem`, `.key`, certificados privados o credenciales cloud.
- Volúmenes de Docker (PostgreSQL, Ollama, artefactos).
- Datasets privados, respaldos de base de datos, archivos de registro o capturas con datos confidenciales.
- Directorios `.git`, `node_modules`, `__pycache__` o archivos compilados.

## Restricciones de seguridad de la aplicación

- La API y el panel se publican **únicamente en localhost** por defecto.
- El acceso de la demo utiliza una API key que el navegador guarda en `sessionStorage`; no publiques esta versión directamente en Internet.
- El acceso de administrador mediante `API_KEY` es adecuado solo para demostraciones locales.
- El código no ha sido sometido a una auditoría de seguridad empresarial ni a pruebas de penetración.
- Las pruebas unitarias no prueban el endurecimiento de una implementación pública.

## Rotación

Si utilizaste credenciales propuestas en un chat, documentación compartida o capturas, genera otras antes de cualquier despliegue público. Guarda las credenciales verdaderas exclusivamente en tu `.env` privado o en un gestor de secretos.

## Comprobación

Desde la raíz del repositorio, ejecuta:

```bash
python scripts/check_publication.py
```

El script detecta ciertos archivos y firmas de secretos. Inspecciona además manualmente los cambios antes de cada `git push`.
