from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.routers.item_router import router as item_router
from app.domain.core.errors import setup_error_handlers
from app.infrastructure.middleware import SecurityMiddleware
from app.infrastructure.config.env_config import config
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Crear aplicación FastAPI
app = FastAPI(
    title="MercadoLibre Items API",
    description="""API RESTful para gestión de productos inspirada en MercadoLibre con middleware de seguridad implementado.

**Características principales:**
- Arquitectura Domain-Driven Design (DDD)
- Middleware de seguridad completo
- Sistema de autenticación por API Key
- Rate limiting por IP
- Headers de seguridad automáticos

**Seguridad:**
- Autenticación por API Key requerida para endpoints protegidos
- Rate limiting: 100 requests por minuto por IP
- Headers de seguridad: CORS, XSS Protection, CSP
- Logging completo de accesos

**API Keys disponibles:**
- `ml-api-key-admin` (rol: admin) - Acceso completo
- `ml-api-key-user` (rol: user) - Endpoints de consulta
- `ml-api-key-readonly` (rol: readonly) - Solo lectura

**Uso de API Keys:**

Método 1 - Header:
```
X-API-Key: ml-api-key-user
```

Método 2 - Query Parameter:
```
?api_key=ml-api-key-user
```

**Códigos de error de seguridad:**
- 401: API Key requerida o inválida
- 403: Permisos insuficientes 
- 429: Rate limit excedido""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "MercadoLibre Items API",
        "email": "api@mercadolibre.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Servidor de desarrollo"
        }
    ],
    tags_metadata=[
        {
            "name": "health",
            "description": "Endpoints de monitoreo y estado del servicio"
        },
        {
            "name": "items",
            "description": "Operaciones CRUD y búsqueda de productos. Incluye detalle, búsqueda avanzada, recomendaciones y filtros."
        },
        {
            "name": "search",
            "description": "Funcionalidades de búsqueda avanzada con múltiples filtros y ordenamiento"
        },
        {
            "name": "recommendations", 
            "description": "Sistema de recomendaciones basado en similitud de productos"
        }
    ]
)

# Configurar CORS desde variables de entorno
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Middleware de seguridad deshabilitado temporalmente para debugging
app.add_middleware(SecurityMiddleware)

# Endpoint de prueba simple (sin middleware)
@app.get("/test")
def test_endpoint():
    return {"status": "working", "message": "Server is responding"}

# Incluir routers
app.include_router(item_router)

# Configurar manejadores de excepciones
setup_error_handlers(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.APP_PORT)



