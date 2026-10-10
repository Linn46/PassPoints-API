# Passpoints API

API desarrollada con FastAPI para el análisis y autenticación mediante contraseñas gráficas Passpoints de cinco puntos.

Actualmente, el proyecto implementa una metodología de análisis basada en triangulación de Delaunay, utilizando métricas geométricas de perímetros y ángulos junto con pruebas estadísticas para identificar patrones potencialmente débiles en las contraseñas gráficas.

El proyecto está organizado para permitir la incorporación futura de otras metodologías de análisis sin mezclar su lógica científica con la metodología actualmente implementada.

## Arquitectura

El proyecto utiliza una arquitectura modular en la que se comparten los componentes generales del sistema, mientras que cada metodología científica mantiene su propia implementación.

    app/
    ├── api/
    ├── application/
    │   └── analysis/
    │       ├── methods/
    │       │   ├── delaunay_statistical/
    │       │   │   ├── service.py
    │       │   │   ├── security.py
    │       │   │   └── triangulation.py
    │       │   │
    │       │   └── mean_distance_convex_hull/
    │       │       └──
    │       │
    │       ├── registry.py
    │       ├── result_mapper.py
    │       ├── security.py
    │       ├── service.py
    │       └── triangulation.py
    │
    ├── core/
    ├── domain/
    ├── geometry/
    ├── infrastructure/
    ├── reporting/
    └── main.py

### Metodología

Una de las metodologias corresponde al análisis basado en:

- Triangulación de Delaunay.
- Perímetros de los triángulos de Delaunay.
- Ángulos máximos.
- Pruebas estadísticas.
- Evaluación de seguridad.
- Clasificación de patrones potencialmente débiles.

Su implementación se encuentra en:

    app/application/analysis/methods/delaunay_statistical/

El proyecto contiene un espacio reservado para incorporar posteriormente otra metodología:

    app/application/analysis/methods/mean_distance_convex_hull/

### Componentes compartidos

Los componentes que son independientes de una metodología específica se reutilizan dentro del sistema. Entre ellos se encuentran:

- Entidades y objetos del dominio.
- Validación de puntos.
- Geometría común.
- Configuración.
- Infraestructura de persistencia.
- Repositorios.
- API.
- Autenticación.
- Utilidades comunes.

La lógica científica específica de cada metodología debe permanecer separada.

## Requisitos

Para ejecutar el proyecto localmente se necesita:

- Python 3.14 o compatible.
- PostgreSQL.
- Git.
- Dependencias especificadas en `requirements.txt`.

Docker también está disponible como alternativa para ejecutar la API.

## Instalación desde cero

### 1. Clonar el proyecto

```
    git clone <repository-url>
    cd passpoints-api
```

Si el repositorio ya fue descargado:

```
    cd passpoints-api
```

### 2. Crear el entorno virtual

```
    python3 -m venv .venv
```

Activar el entorno virtual:

```
    source .venv/bin/activate
```

### 3. Instalar las dependencias

```
    python -m pip install --upgrade pip

    python -m pip install -r requirements.txt
```

## Configuración de PostgreSQL

El proyecto utiliza PostgreSQL para la persistencia de los datos.

Antes de ejecutar las migraciones, PostgreSQL debe estar instalado y ejecutándose.

### Crear la base de datos

Crear una base de datos llamada `passpoints`:

```
    CREATE DATABASE passpoints;
```

El usuario y la contraseña utilizados dependen de la instalación local de PostgreSQL.

### Configurar `DATABASE_URL`

En Bash:

```
    export DATABASE_URL="postgresql+psycopg://<usuario>:<clave>@localhost:5432/passpoints"
```

Sustituye `<usuario>` y `<clave>` por las credenciales correspondientes a tu instalación de PostgreSQL.

No coloques credenciales reales en el README ni las subas al repositorio.
Puedes comprobar que la variable quedó configurada con:

```
    echo "$DATABASE_URL"
```

### Comprobar la conexión

Ejecuta:

```
    python -c "import os; from sqlalchemy import create_engine, text; e=create_engine(os.environ['DATABASE_URL']); print(e.connect().execute(text('select 1')).scalar()); e.dispose()"
```

Si la conexión es correcta, debe mostrarse:

    1

## Configuración de autenticación

La autenticación utiliza `AUTH_TOKEN_SECRET` para la generación y validación de los tokens.

Genera un secreto aleatorio:

```
    export AUTH_TOKEN_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
```

Puedes comprobar que existe con:

```
    echo "$AUTH_TOKEN_SECRET"
```

No compartas este valor ni lo almacenes directamente en el repositorio.

## Ejecutar las migraciones

Una vez configurada la conexión con PostgreSQL:

```
    python -m alembic upgrade head
```

Este comando aplica las migraciones existentes y crea o actualiza las tablas necesarias de la base de datos.

## Ejecutar la API

Con el entorno virtual activado y las variables de entorno configuradas:

```
    uvicorn app.main:app --reload --port 8001
```

La API estará disponible en:

    http://localhost:8001

La documentación interactiva de FastAPI estará disponible en:

    http://localhost:8001/docs

También puede consultarse el esquema OpenAPI en:

    http://localhost:8001/openapi.json

## Frontend

El proyecto contiene un frontend ubicado en:

    frontend/

Para ejecutarlo mediante el servidor HTTP incluido en Python:

    python -m http.server 5500 -d frontend

El frontend estará disponible en:

    http://localhost:5500

La API debe permanecer ejecutándose en otra terminal.

## Endpoints principales

### Health check

    GET /health

Comprueba que la API se encuentra disponible.

### Análisis Passpoints

    POST /api/v1/analysis

Analiza una contraseña gráfica Passpoints formada por cinco puntos.

El análisis valida los puntos y aplica la metodología basada en Delaunay para obtener las métricas y clasificación correspondientes.

### Registro

    POST /auth/register

Registra un usuario y su credencial gráfica Passpoints.

La contraseña gráfica debe estar formada por cinco puntos y no puede ser aceptada si el análisis determina que corresponde a un patrón débil según la metodología actualmente implementada.

### Login

    POST /auth/login

Autentica al usuario mediante su credencial Passpoints.

Cuando la autenticación es correcta, el sistema devuelve un token de autenticación.

### Documentación OpenAPI

    GET /docs

Proporciona la documentación interactiva de los endpoints mediante Swagger UI.

## Análisis de una contraseña Passpoints

La metodología actualmente implementada sigue, de forma general, este flujo:

    Cinco puntos
         │
         ▼
      Validación
         │
         ▼
    Triangulación
     de Delaunay
         │
         ├──────────────┐
         ▼              ▼
     Perímetros      Ángulos
         │              │
         └──────┬───────┘
                ▼
       Pruebas estadísticas
                │
                ▼
        Evaluación de patrones
                │
                ▼
         Resultado del análisis

La aplicación trabaja con contraseñas formadas por exactamente cinco puntos.

Las coordenadas recibidas corresponden a posiciones dentro de la imagen utilizada por el sistema.

## Ejemplo de petición de análisis

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

Los puntos deben cumplir las restricciones de validación establecidas por la API.

## Autenticación Passpoints

La autenticación utiliza la contraseña gráfica como credencial.

Durante el registro se almacenan los datos necesarios para verificar posteriormente la credencial sin guardar directamente los puntos originales como una contraseña en texto plano.

El sistema utiliza un `verifier` para la credencial gráfica y mecanismos de protección criptográfica para su almacenamiento.

El login devuelve un bearer token JWT cuando la autenticación es exitosa.

La configuración necesaria para ejecutar los flujos de autenticación incluye:

    export DATABASE_URL="postgresql+psycopg://<usuario>:<clave>@localhost:5432/passpoints"
    export AUTH_TOKEN_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"

## Pruebas

Para ejecutar la suite de pruebas:

    python -m pytest -v

También se pueden ejecutar grupos específicos de pruebas:

    python -m pytest tests/unit -v

Las pruebas del proyecto incluyen diferentes niveles de validación, entre ellos:

- Pruebas unitarias.
- Pruebas de integración.
- Pruebas de geometría.
- Pruebas de análisis.
- Pruebas estadísticas.
- Pruebas de rendimiento.

Las pruebas que requieren PostgreSQL necesitan que `DATABASE_URL` esté correctamente configurada.

## Estado actual

La metodología científica actualmente disponible es la basada en Delaunay.

La arquitectura está preparada para incorporar posteriormente otras metodologías de análisis manteniendo separada su lógica científica.

La segunda metodología no forma parte todavía de la implementación actual.

El estado de la suite completa de pruebas puede depender de la configuración local de PostgreSQL y de los contratos actuales de autenticación. Por ello, antes de considerar una ejecución completamente verificada, deben configurarse las variables de entorno y ejecutarse las pruebas en el entorno correspondiente.

## Docker

El proyecto incluye un `Dockerfile`.

Construir la imagen:

    docker build -t passpoints-api .

Ejecutar el contenedor:

    docker run --rm -p 8000:8000 passpoints-api

Si la ejecución mediante Docker requiere variables de entorno, deben proporcionarse al contenedor mediante la configuración correspondiente de Docker.

## Flujo de desarrollo recomendado

Para trabajar con el proyecto desde cero:

```
    cd passpoints-api

    python3 -m venv .venv
    source .venv/bin/activate

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

    export DATABASE_URL="postgresql+psycopg://<usuario>:<clave>@localhost:5432/passpoints"
    export AUTH_TOKEN_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"

    python -c "import os; from sqlalchemy import create_engine, text; e=create_engine(os.environ['DATABASE_URL']); print(e.connect().execute(text('select 1')).scalar()); e.dispose()"

    python -m alembic upgrade head

    python -m pytest -v

    uvicorn app.main:app --reload --port 8001
```

En otra terminal, con el entorno virtual activado:

```
    python -m http.server 5500 -d frontend
```

Después:

    API:
    http://localhost:8001

    Swagger:
    http://localhost:8001/docs

    Frontend:
    http://localhost:5500

## Buenas prácticas

- No almacenar contraseñas, claves de PostgreSQL ni secretos en el repositorio.
- No publicar `DATABASE_URL` con credenciales reales.
- No publicar `AUTH_TOKEN_SECRET`.
- Mantener separada la lógica científica específica de cada metodología.
- Reutilizar componentes comunes cuando realmente sean compartidos.
- No duplicar infraestructura innecesariamente.
- Mantener las pruebas asociadas a cada componente y metodología.
- Ejecutar las pruebas antes de realizar cambios importantes en el proyecto.

## Licencia

Este proyecto forma parte del trabajo académico relacionado con el análisis y autenticación mediante contraseñas gráficas Passpoints.
