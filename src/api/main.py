from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routes import queries, system, metadata

def custom_openapi():
    """Generar documentación OpenAPI personalizada con información detallada."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="RAG Legal API",
        version="1.0.0",
        description="""
# 🏛️ RAG Legal API - Sistema de Recuperación Augmentada por Generación

## 📋 Descripción General

Esta API proporciona capacidades avanzadas de búsqueda semántica y gestión de documentos legales utilizando técnicas de Recuperación Augmentada por Generación (RAG). El sistema permite consultar documentos legales de manera inteligente, extraer información relevante y mantener un historial de consultas.

## 🚀 Características Principales

- **🔍 Consultas Semánticas**: Búsqueda inteligente en documentos legales
- **📚 Gestión de Metadatos**: Organización y filtrado de documentos
- **📊 Historial de Consultas**: Seguimiento de búsquedas realizadas
- **🏥 Filtros Avanzados**: Búsqueda por tipo de documento, tribunal, fechas
- **📈 Estadísticas del Sistema**: Monitoreo de uso y rendimiento

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **Pandas**: Procesamiento de datos y metadatos
- **Pydantic**: Validación de datos y serialización
- **Uvicorn**: Servidor ASGI de alto rendimiento

## 📖 Guía de Uso

### Autenticación
Actualmente la API no requiere autenticación para el MVP. En futuras versiones se implementará OAuth2.

### Rate Limiting
- **Consultas**: 100 requests por minuto
- **Metadatos**: 200 requests por minuto
- **Sistema**: 50 requests por minuto

### Formatos de Respuesta
Todas las respuestas están en formato JSON con codificación UTF-8.

### Códigos de Estado HTTP
- `200`: Operación exitosa
- `400`: Error en los datos de entrada
- `404`: Recurso no encontrado
- `422`: Error de validación
- `500`: Error interno del servidor

## 🔗 Endpoints Disponibles

### Consultas (`/api/v1/queries`)
- `POST /queries`: Realizar consultas semánticas
- `GET /queries/history`: Obtener historial de consultas

### Metadatos (`/api/v1/metadata`)
- `GET /metadata/documents`: Listar documentos con filtros
- `GET /metadata/documents/{id}`: Obtener documento específico
- `GET /metadata/documents/{id}/summary`: Resumen de documento

### Sistema (`/api/v1/system`)
- `GET /system/health`: Estado de salud del sistema
- `GET /system/info`: Información general del sistema
- `GET /system/stats`: Estadísticas de uso

## 📝 Ejemplos de Uso

### Consulta Semántica
```bash
curl -X POST "http://localhost:8001/api/v1/queries" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es el demandante del expediente?",
    "n_results": 5
  }'
```

### Obtener Metadatos
```bash
curl "http://localhost:8001/api/v1/metadata/documents?page=1&page_size=10&document_type=Sentencia"
```

## 🐛 Reportar Problemas

Si encuentras algún problema o tienes sugerencias, por favor:
1. Revisa la documentación completa en `/docs`
2. Verifica los logs del servidor
3. Contacta al equipo de desarrollo

## 📄 Licencia

Este proyecto es parte de un MVP para demostración de capacidades RAG en documentos legales.

## 🔄 Versiones

- **v1.0.0**: MVP inicial con funcionalidades básicas
- **Próximas**: Autenticación, más tipos de documentos, análisis avanzado
        """,
        routes=app.routes,
    )
    
    # Agregar información de contacto
    openapi_schema["info"]["contact"] = {
        "name": "Equipo RAG Legal",
        "email": "support@raglegal.com",
        "url": "https://github.com/rag-legal/api"
    }
    
    # Agregar licencia
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # Agregar servidores
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8001",
            "description": "Servidor de desarrollo local"
        },
        {
            "url": "https://api.raglegal.com",
            "description": "Servidor de producción"
        }
    ]
    
    # Agregar tags con descripciones detalladas
    openapi_schema["tags"] = [
        {
            "name": "Consultas",
            "description": "Endpoints para realizar consultas semánticas en documentos legales y gestionar el historial de búsquedas.",
            "externalDocs": {
                "description": "Guía de consultas semánticas",
                "url": "https://docs.raglegal.com/queries"
            }
        },
        {
            "name": "Metadatos",
            "description": "Gestión y consulta de metadatos de documentos legales, incluyendo filtros, paginación y resúmenes.",
            "externalDocs": {
                "description": "Guía de metadatos",
                "url": "https://docs.raglegal.com/metadata"
            }
        },
        {
            "name": "Sistema",
            "description": "Endpoints para monitorear el estado del sistema, obtener información general y estadísticas de uso.",
            "externalDocs": {
                "description": "Monitoreo del sistema",
                "url": "https://docs.raglegal.com/system"
            }
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="RAG Legal API",
    description="API REST para sistema RAG de documentos legales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 3,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "syntaxHighlight.theme": "monokai"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Incluir routers
app.include_router(system.router)
app.include_router(queries.router)
app.include_router(metadata.router)

@app.get("/", 
    summary="Información General",
    description="Endpoint raíz que proporciona información básica sobre la API RAG Legal.",
    response_description="Información general del sistema",
    tags=["Sistema"])
async def root():
    """
    # 🏠 Página Principal
    
    Bienvenido a la API RAG Legal. Este endpoint proporciona información básica sobre el sistema.
    
    ## Respuesta
    
    La respuesta incluye un mensaje de bienvenida y descripción del sistema.
    
    ## Ejemplo de Respuesta
    
    ```json
    {
        "message": "RAG Legal API - Sistema de Recuperación Augmentada por Generación"
    }
    ```
    """
    return {
        "message": "RAG Legal API - Sistema de Recuperación Augmentada por Generación",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "endpoints": {
            "queries": "/api/v1/queries",
            "metadata": "/api/v1/metadata",
            "system": "/api/v1/system"
        }
    }

# Configurar OpenAPI personalizado
app.openapi = custom_openapi
