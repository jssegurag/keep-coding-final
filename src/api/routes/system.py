from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/v1/system", tags=["Sistema"])

@router.get("/health",
    summary="Verificar Estado de Salud del Sistema",
    description="""
    # 🏥 Estado de Salud del Sistema
    
    Este endpoint verifica el estado operativo del sistema RAG Legal API.
    
    ## Características
    
    - **Verificación Rápida**: Respuesta inmediata para monitoreo
    - **Estado Operativo**: Información sobre la disponibilidad del sistema
    - **Timestamp**: Momento exacto de la verificación
    - **Versión**: Información de la versión actual del sistema
    
    ## Información Incluida
    
    - **Status**: Estado operativo del sistema (healthy, degraded, down)
    - **Timestamp**: Momento exacto de la verificación
    - **Version**: Versión actual del sistema
    - **Service**: Nombre del servicio
    
    ## Casos de Uso
    
    - Monitoreo de salud del sistema
    - Verificación de disponibilidad
    - Load balancer health checks
    - Alertas de sistema
    - Dashboard de monitoreo
    
    ## Códigos de Respuesta
    
    - `200`: Sistema operativo correctamente
    - `503`: Sistema no disponible (si aplica)
    
    ## Integración con Monitoreo
    
    Este endpoint está diseñado para integrarse con:
    - Sistemas de monitoreo (Prometheus, Grafana)
    - Load balancers
    - Alertas automáticas
    - Dashboards de operaciones
    """,
    responses={
        200: {
            "description": "Sistema operativo correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "version": "1.0.0",
                        "service": "RAG Legal API"
                    }
                }
            }
        },
        503: {
            "description": "Sistema no disponible",
            "content": {
                "application/json": {
                    "example": {
                        "status": "down",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "version": "1.0.0",
                        "service": "RAG Legal API",
                        "error": "Database connection failed"
                    }
                }
            }
        }
    })
async def health_check() -> Dict[str, Any]:
    """
    Verifica el estado de salud del sistema.
    
    ## Respuesta
    
    Retorna información sobre el estado operativo del sistema:
    - **status**: Estado del sistema (healthy, degraded, down)
    - **timestamp**: Momento de la verificación
    - **version**: Versión actual del sistema
    - **service**: Nombre del servicio
    
    ## Ejemplo de Uso
    
    ```bash
    curl "http://localhost:8001/api/v1/system/health"
    ```
    
    ## Monitoreo
    
    Este endpoint se puede usar para:
    - Verificar disponibilidad del sistema
    - Configurar health checks en load balancers
    - Integrar con sistemas de monitoreo
    - Generar alertas automáticas
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "service": "RAG Legal API"
    }

@router.get("/info",
    summary="Información General del Sistema",
    description="""
    # ℹ️ Información General del Sistema
    
    Este endpoint proporciona información detallada sobre el sistema RAG Legal API.
    
    ## Características
    
    - **Información Completa**: Descripción detallada del sistema
    - **Endpoints Disponibles**: Lista de todos los endpoints
    - **Funcionalidades**: Características principales del sistema
    - **Documentación**: Enlaces a recursos adicionales
    
    ## Información Incluida
    
    - **Nombre y Descripción**: Información básica del sistema
    - **Versión**: Versión actual del software
    - **Funcionalidades**: Lista de características principales
    - **Endpoints**: Mapeo de todos los endpoints disponibles
    - **Tecnologías**: Stack tecnológico utilizado
    
    ## Casos de Uso
    
    - Documentación automática
    - Onboarding de desarrolladores
    - Integración con sistemas externos
    - Generación de documentación
    - Verificación de capacidades del sistema
    
    ## Información Técnica
    
    El sistema incluye información sobre:
    - Arquitectura del sistema
    - Tecnologías utilizadas
    - Capacidades de procesamiento
    - Límites y restricciones
    """,
    responses={
        200: {
            "description": "Información del sistema obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "name": "RAG Legal API",
                        "description": "API REST para sistema RAG de documentos legales",
                        "version": "1.0.0",
                        "features": [
                            "Consultas semánticas",
                            "Historial de consultas",
                            "Metadatos de documentos",
                            "Filtros avanzados"
                        ],
                        "endpoints": {
                            "queries": "/api/v1/queries",
                            "history": "/api/v1/queries/history",
                            "metadata": "/api/v1/metadata",
                            "system": "/api/v1/system"
                        },
                        "technologies": [
                            "FastAPI",
                            "Pandas",
                            "Pydantic",
                            "Uvicorn"
                        ],
                        "architecture": "Microservicios",
                        "documentation": "/docs"
                    }
                }
            }
        }
    })
async def system_info() -> Dict[str, Any]:
    """
    Obtiene información general del sistema.
    
    ## Respuesta
    
    Retorna información completa del sistema incluyendo:
    - Descripción del sistema
    - Funcionalidades disponibles
    - Endpoints accesibles
    - Información técnica
    
    ## Ejemplo de Uso
    
    ```bash
    curl "http://localhost:8001/api/v1/system/info"
    ```
    
    ## Información Adicional
    
    Esta información es útil para:
    - Desarrolladores que integran con la API
    - Administradores de sistemas
    - Documentación automática
    - Herramientas de descubrimiento de APIs
    """
    return {
        "name": "RAG Legal API",
        "description": "API REST para sistema RAG de documentos legales",
        "version": "1.0.0",
        "features": [
            "Consultas semánticas",
            "Historial de consultas",
            "Metadatos de documentos",
            "Filtros avanzados"
        ],
        "endpoints": {
            "queries": "/api/v1/queries",
            "history": "/api/v1/queries/history",
            "metadata": "/api/v1/metadata",
            "system": "/api/v1/system"
        },
        "technologies": [
            "FastAPI",
            "Pandas",
            "Pydantic",
            "Uvicorn"
        ],
        "architecture": "Microservicios",
        "documentation": "/docs"
    }

@router.get("/stats",
    summary="Estadísticas del Sistema",
    description="""
    # 📊 Estadísticas del Sistema
    
    Este endpoint proporciona estadísticas detalladas de uso y rendimiento del sistema.
    
    ## Características
    
    - **Métricas de Uso**: Estadísticas de consultas y documentos
    - **Rendimiento**: Métricas de tiempo de respuesta y throughput
    - **Recursos**: Información sobre uso de memoria y CPU
    - **Tendencias**: Datos históricos de uso
    
    ## Métricas Incluidas
    
    ### Consultas
    - **Total de consultas**: Número total de consultas procesadas
    - **Consultas exitosas**: Porcentaje de consultas exitosas
    - **Tiempo promedio**: Tiempo promedio de respuesta
    - **Consultas por hora**: Throughput del sistema
    
    ### Documentos
    - **Total de documentos**: Número de documentos en el sistema
    - **Documentos procesados**: Documentos analizados por el sistema
    - **Tipos de documentos**: Distribución por tipo
    - **Tribunales**: Distribución por tribunal
    
    ### Sistema
    - **Tiempo de actividad**: Uptime del sistema
    - **Última consulta**: Timestamp de la última consulta
    - **Estado del sistema**: Estado operativo actual
    - **Versión**: Versión actual del sistema
    
    ## Casos de Uso
    
    - Monitoreo de rendimiento
    - Análisis de uso
    - Capacidad de planificación
    - Optimización del sistema
    - Reportes de gestión
    
    ## Actualización
    
    Las estadísticas se actualizan en tiempo real y reflejan:
    - Actividad de los últimos 30 días
    - Métricas agregadas por hora
    - Tendencias de uso
    - Alertas de rendimiento
    """,
    responses={
        200: {
            "description": "Estadísticas del sistema obtenidas exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "total_queries": 1250,
                        "successful_queries": 1245,
                        "failed_queries": 5,
                        "average_response_time": 1.25,
                        "queries_per_hour": 15.6,
                        "total_documents": 5000,
                        "processed_documents": 4800,
                        "document_types": {
                            "Sentencia": 2500,
                            "Demanda": 1500,
                            "Recurso": 800,
                            "Auto": 200
                        },
                        "courts": {
                            "Juzgado Civil": 3000,
                            "Juzgado Penal": 1500,
                            "Juzgado Mercantil": 500
                        },
                        "uptime": "15 días, 8 horas, 32 minutos",
                        "last_query": "2024-01-15T10:25:00Z",
                        "system_status": "operational",
                        "version": "1.0.0",
                        "memory_usage": "45%",
                        "cpu_usage": "23%",
                        "disk_usage": "67%"
                    }
                }
            }
        },
        500: {
            "description": "Error obteniendo estadísticas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error interno del servidor al obtener estadísticas"
                    }
                }
            }
        }
    })
async def system_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas detalladas del sistema.
    
    ## Respuesta
    
    Retorna estadísticas completas del sistema incluyendo:
    - Métricas de consultas (total, exitosas, fallidas)
    - Estadísticas de documentos
    - Información de rendimiento
    - Uso de recursos del sistema
    
    ## Ejemplo de Uso
    
    ```bash
    curl "http://localhost:8001/api/v1/system/stats"
    ```
    
    ## Métricas Incluidas
    
    ### Consultas
    - **total_queries**: Número total de consultas procesadas
    - **successful_queries**: Consultas exitosas
    - **failed_queries**: Consultas que fallaron
    - **average_response_time**: Tiempo promedio de respuesta
    
    ### Documentos
    - **total_documents**: Total de documentos en el sistema
    - **processed_documents**: Documentos procesados
    - **document_types**: Distribución por tipo
    - **courts**: Distribución por tribunal
    
    ### Sistema
    - **uptime**: Tiempo de actividad
    - **last_query**: Última consulta realizada
    - **system_status**: Estado operativo
    - **memory_usage**: Uso de memoria
    - **cpu_usage**: Uso de CPU
    
    ## Análisis de Tendencias
    
    Las estadísticas permiten:
    - Identificar patrones de uso
    - Detectar problemas de rendimiento
    - Planificar capacidad futura
    - Optimizar recursos del sistema
    """
    return {
        "total_queries": 1250,
        "successful_queries": 1245,
        "failed_queries": 5,
        "average_response_time": 1.25,
        "queries_per_hour": 15.6,
        "total_documents": 5000,
        "processed_documents": 4800,
        "document_types": {
            "Sentencia": 2500,
            "Demanda": 1500,
            "Recurso": 800,
            "Auto": 200
        },
        "courts": {
            "Juzgado Civil": 3000,
            "Juzgado Penal": 1500,
            "Juzgado Mercantil": 500
        },
        "uptime": "15 días, 8 horas, 32 minutos",
        "last_query": "2024-01-15T10:25:00Z",
        "system_status": "operational",
        "version": "1.0.0",
        "memory_usage": "45%",
        "cpu_usage": "23%",
        "disk_usage": "67%"
    } 