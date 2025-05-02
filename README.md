# PVC Shop API - Backend (En Construcción 🚧)

Este proyecto es una API REST para una tienda de productos de ferreteria, desarrollada con FastAPI y PostgreSQL, utilizando Supabase como proveedor de base de datos.

## Estado del Proyecto

⚠️ **AVISO: Este proyecto está actualmente en desarrollo activo** ⚠️

## Características Principales

- 🔐 Autenticación y autorización de usuarios
- 👥 Gestión de diferentes roles de usuario (cliente, distribuidor, administrador, empleado)
- 📦 Gestión de productos y categorías
- 🛒 Sistema de pedidos
- 📊 Inventario y stock
- 🏭 Gestión de producción
- 📧 Sistema de notificaciones por email
- 🔍 Búsqueda y filtrado avanzado
- 📱 API RESTful completamente documentada

## Requisitos Técnicos

* [Python 3.9+](https://www.python.org/)
* [Docker](https://www.docker.com/) (opcional)
* [uv](https://docs.astral.sh/uv/) para gestión de paquetes Python
* [PostgreSQL](https://www.postgresql.org/) (se usa Supabase en producción)

## Configuración del Entorno de Desarrollo

1. Clonar el repositorio:
```bash
git clone [url-del-repositorio]
cd pipe-python-shop
```

2. Crear y activar el entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
uv sync
```

4. Crear archivo .env en la raíz del proyecto:
```env
# Environment
ENVIRONMENT=development

# Database settings
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=pvc_shop
POSTGRES_PORT=5432

# Security
SECRET_KEY=your_secret_key

# Admin user
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=your_password
```

5. Inicializar la base de datos:
```bash
alembic upgrade head
```

6. Ejecutar el servidor de desarrollo:
```bash
uvicorn app.main:app --reload
```

## Estructura del Proyecto

```
app/
├── api/              # Endpoints de la API
├── core/             # Configuración central
├── crud/            # Operaciones CRUD
├── models/          # Modelos SQLModel
├── schemas/         # Esquemas Pydantic
├── tests/           # Tests
└── utils/           # Utilidades
```

## API Endpoints

La documentación completa de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Despliegue

El proyecto está configurado para desplegarse en Supabase para la base de datos y puede desplegarse en cualquier plataforma que soporte Docker.

### Variables de Entorno para Producción

Asegúrate de configurar las siguientes variables de entorno en producción:

```env
ENVIRONMENT=production
POSTGRES_SERVER=aws-0-us-east-2.pooler.supabase.com
POSTGRES_USER=your_supabase_user
POSTGRES_PASSWORD=your_supabase_password
POSTGRES_DB=your_supabase_db
POSTGRES_PORT=5432
SECRET_KEY=your_production_secret_key
```

## Tests

Ejecutar los tests:
```bash
pytest
```

