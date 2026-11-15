# Publicar TITAN AI en GitHub (Windows / PowerShell)

Este ZIP está preparado como **copia pública**. No incluye secretos, datos de ejecución ni el `.env` local.

## Antes de publicar

1. Extrae el ZIP en una **carpeta nueva**, no encima de tu instalación que contiene `.env`.
2. Ejecuta `python scripts/check_publication.py`.
3. Abre `README.md`, `compose.yaml`, `.env.example` y revisa cualquier modificación propia.
4. No añadas archivos personales, capturas con tokens, registros de consola ni carpetas con datos privados.
5. Nunca subas tu `.env`, ni siquiera mediante la carga web de GitHub (que no aplica `.gitignore` automáticamente).
6. Si alguna clave se ha mostrado o compartido anteriormente, reemplázala antes de usar la aplicación fuera de pruebas locales.

## Subir con Git

En una carpeta descomprimida nueva:

```powershell
git init
git add .
git status --short
git commit -m "Add TITAN AI engineering portfolio"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/titan-ai.git
git push -u origin main
```

Crea antes un repositorio vacío en GitHub. `TU_USUARIO` es un marcador, no una dirección real. Comprueba `git status` antes de `git commit`.

## Si tu .env estuvo en un repositorio previo

Borrarlo o añadirlo a `.gitignore` NO lo quita del historial de Git. Hay que revocar/rotar las claves y sanear el historial o utilizar este directorio limpio en un repositorio nuevo.

## Alcance de la revisión

El chequeo detecta nombres de archivos privados y varias firmas de credenciales. No sustituye una auditoría de seguridad ni garantiza la ausencia absoluta de secretos.
