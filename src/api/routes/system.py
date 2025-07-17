from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/v1/system", tags=["Sistema"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Verificar el estado de salud del sistema."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "service": "RAG Legal API"
    }

@router.get("/info")
async def system_info() -> Dict[str, Any]:
    """Obtener información del sistema."""
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
        }
    }

@router.get("/stats")
async def system_stats() -> Dict[str, Any]:
    """Obtener estadísticas del sistema."""
    return {
        "total_queries": 0,  # En implementación real, consultaría la base de datos
        "total_documents": 0,  # En implementación real, consultaría la base de datos
        "uptime": "0:00:00",  # En implementación real, calcularía el tiempo de actividad
        "last_query": None,
        "system_status": "operational"
    } 