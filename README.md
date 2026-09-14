# Passpoints API

API FastAPI para analizar contraseñas gráficas Passpoints de cinco puntos.
El análisis combina triangulación de Delaunay con pruebas estadísticas basadas
en perímetros y ángulos para identificar patrones potencialmente frágiles.

## Requisitos

- Python 3.14 o compatible
- Dependencias de `requirements.txt`

## Ejecución local

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`.

## Docker

```powershell
docker build -t passpoints-api .
docker run --rm -p 8000:8000 passpoints-api
```

## Endpoints

- `GET /health`: verifica que la API esté disponible.
- `POST /api/v1/analysis`: analiza cinco puntos Passpoints.
- `GET /docs`: documentación OpenAPI interactiva.

Ejemplo de petición:

```json
{
  "points": [
    { "x": 100, "y": 100 },
    { "x": 500, "y": 100 },
    { "x": 500, "y": 500 },
    { "x": 100, "y": 500 },
    { "x": 300, "y": 300 }
  ],
  "image_width": 1920,
  "image_height": 1080,
  "alpha": 0.05
}
```

Los tamaños de imagen soportados por el test de perímetros son `800x480`,
`1366x768` y `1920x1080`.

## Pruebas

```powershell
.venv\Scripts\python.exe -m pytest -v
```

La suite incluye pruebas unitarias, de integración y una comprobación básica
de rendimiento para análisis repetidos.
