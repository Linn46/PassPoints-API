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
$env:DATABASE_URL = "postgresql+psycopg://<usuario>:<clave>@localhost:5432/passpoints"
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$bytes = New-Object byte[] 48
$rng.GetBytes($bytes)
$env:AUTH_TOKEN_SECRET = [Convert]::ToBase64String($bytes)
python -c "import os; from sqlalchemy import create_engine, text; e=create_engine(os.environ['DATABASE_URL']); print(e.connect().execute(text('select 1')).scalar()); e.dispose()"
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Sustituye `<usuario>` y `<clave>` por los de PostgreSQL. Ejecuta todos los
comandos en la misma ventana de PowerShell y deja esa ventana abierta mientras
Uvicorn esté corriendo. Si detienes y vuelves a arrancar la API, conserva el
mismo `AUTH_TOKEN_SECRET` para que los tokens emitidos sigan siendo válidos.

La documentación interactiva queda disponible en `http://localhost:8001/docs`.

Para el registro y login gráfico configura `DATABASE_URL` y `AUTH_TOKEN_SECRET`
(al menos 32 bytes aleatorios). El registro solicita nombre y correo; la imagen
y los cinco puntos son la credencial Passpoints. No se pide contraseña textual
en esta fase.

## Docker

```powershell
docker build -t passpoints-api .
docker run --rm -p 8000:8000 passpoints-api
```

## Endpoints

- `GET /health`: verifica que la API esté disponible.
- `POST /api/v1/analysis`: analiza cinco puntos Passpoints.
- `POST /auth/register`: registra nombre, correo e imagen con cinco puntos.
- `POST /auth/login`: autentica con correo e imagen con cinco puntos; devuelve
  un bearer JWT.
- `GET /docs`: documentación OpenAPI interactiva.

Registro y login reciben `username`, `password`, `image_id`, dimensiones de la
imagen y cinco puntos en coordenadas de píxeles. El registro rechaza patrones
clasificados como débiles. Passpoints normaliza las coordenadas a una grilla
relativa de 20 × 20 y guarda solo un verifier Argon2id; el token se devuelve
solo en el login.

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

Registro recibe `username`, `email`, `image_id`, dimensiones y cinco puntos en
píxeles. Login recibe `email`, `image_id`, dimensiones y cinco puntos. Los
tamaños de imagen soportados por el test de perímetros son `800x480`,
`1366x768` y `1920x1080`.

## Pruebas

```powershell
.venv\Scripts\python.exe -m pytest -v
```

La suite incluye pruebas unitarias, de integración y una comprobación básica
de rendimiento para análisis repetidos.
