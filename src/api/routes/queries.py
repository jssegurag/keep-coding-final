from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.queries import QueryRequest, QueryResponse, QueryHistoryResponse
from ..services.query_history_service import QueryHistoryService
from ...query.query_handler import QueryHandler

router = APIRouter(prefix="/api/v1/queries", tags=["Consultas"])

# Instancia global para persistencia en memoria
history_service_instance = QueryHistoryService()

def get_query_handler() -> QueryHandler:
    return QueryHandler()

def get_history_service() -> QueryHistoryService:
    return history_service_instance

@router.post("/", response_model=QueryResponse)
async def create_query(
    query_request: QueryRequest,
    query_handler: QueryHandler = Depends(get_query_handler),
    history_service: QueryHistoryService = Depends(get_history_service)
) -> QueryResponse:
    """Realizar consulta semántica individual."""
    try:
        # Procesar consulta usando el QueryHandler existente
        result = query_handler.handle_query(
            query=query_request.query,
            n_results=query_request.n_results
        )
        
        # Crear respuesta
        response = QueryResponse(
            query=query_request.query,
            response=result["response"],
            entities=result["entities"],
            filters_used=result["filters_used"],
            search_results_count=result["search_results_count"],
            source_info=result["source_info"],
            enriched_metadata=result["enriched_metadata"],
            timestamp=datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
        )
        
        # Guardar en historial
        history_service.add_query(
            query=query_request.query,
            response=result["response"],
            search_results_count=result["search_results_count"],
            source_info=result["source_info"],
            entities=result["entities"],
            filters_used=result["filters_used"]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=10, description="Tamaño de página"),
    query_filter: Optional[str] = Query(None, description="Filtro de texto para buscar en consultas"),
    history_service: QueryHistoryService = Depends(get_history_service)
) -> QueryHistoryResponse:
    """Obtener historial de consultas con paginación."""
    try:
        return history_service.get_history(
            page=page,
            page_size=page_size,
            query_filter=query_filter
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.get("/history/statistics")
async def get_history_statistics(
    history_service: QueryHistoryService = Depends(get_history_service)
) -> Dict[str, Any]:
    """Obtener estadísticas del historial de consultas."""
    try:
        return history_service.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

@router.delete("/history/{query_id}")
async def delete_query_from_history(
    query_id: str,
    history_service: QueryHistoryService = Depends(get_history_service)
) -> Dict[str, str]:
    """Eliminar una consulta específica del historial."""
    try:
        success = history_service.delete_query(query_id)
        if not success:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        return {"message": "Consulta eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando consulta: {str(e)}")

@router.delete("/history")
async def clear_query_history(
    history_service: QueryHistoryService = Depends(get_history_service)
) -> Dict[str, str]:
    """Eliminar todo el historial de consultas."""
    try:
        count = history_service.clear_history()
        return {"message": f"Historial eliminado exitosamente. {count} consultas eliminadas."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando historial: {str(e)}") 