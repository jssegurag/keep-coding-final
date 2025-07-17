from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from ..models.queries import QueryHistoryItem, QueryHistoryResponse, QueryResponse

# Variable global para historial (singleton simple)
_GLOBAL_HISTORY: List[QueryHistoryItem] = []

class QueryHistoryService:
    def __init__(self):
        # Usar la variable global para el historial
        self._history = _GLOBAL_HISTORY
    
    def add_query(self, query: str, response: str, search_results_count: int, 
                  source_info: Dict[str, Any], entities: Dict[str, Any] = None, 
                  filters_used: Dict[str, Any] = None) -> str:
        """Agregar una nueva consulta al historial."""
        query_id = str(uuid.uuid4())
        
        history_item = QueryHistoryItem(
            id=query_id,
            query=query,
            response=response,
            timestamp=datetime.now(),
            search_results_count=search_results_count,
            source_info=source_info,
            entities=entities or {},
            filters_used=filters_used or {}
        )
        
        self._history.append(history_item)
        return query_id
    
    def add_query_response(self, query_response: QueryResponse) -> str:
        """Agregar una QueryResponse al historial."""
        query_id = str(uuid.uuid4())
        
        history_item = QueryHistoryItem(
            id=query_id,
            query=query_response.query,
            response=query_response.response,
            timestamp=query_response.timestamp,
            search_results_count=query_response.search_results_count,
            source_info=query_response.source_info,
            entities=query_response.entities,
            filters_used=query_response.filters_used
        )
        
        self._history.append(history_item)
        return query_id
    
    def get_current_timestamp(self) -> datetime:
        """Obtener timestamp actual."""
        return datetime.now()
    
    def get_query_history(self, page: int = 1, page_size: int = 10) -> QueryHistoryResponse:
        """Obtener historial de consultas con paginación."""
        return self.get_history(page=page, page_size=page_size)
    
    def get_history(self, page: int =1, page_size: int = 10, 
                   query_filter: Optional[str] = None) -> QueryHistoryResponse:
        """Obtener historial de consultas con paginación."""
        filtered_history = self._history
        
        # Aplicar filtro por texto si se especifica
        if query_filter:
            filtered_history = [
                item for item in self._history 
                if query_filter.lower() in item.query.lower() or 
                   query_filter.lower() in item.response.lower()
            ]
        
        # Ordenar por timestamp descendente (más reciente primero)
        filtered_history.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Calcular paginación
        total_count = len(filtered_history)
        total_pages = (total_count + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Obtener elementos de la página actual
        page_items = filtered_history[start_idx:end_idx]
        
        return QueryHistoryResponse(
            queries=page_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def get_query_by_id(self, query_id: str) -> Optional[QueryHistoryItem]:
        """Obtener una consulta específica por ID."""
        for item in self._history:
            if item.id == query_id:
                return item
        return None
    
    def delete_query(self, query_id: str) -> bool:
        """Eliminar una consulta del historial."""
        for i, item in enumerate(self._history):
            if item.id == query_id:
                del self._history[i]
                return True
        return False    
    
    def clear_history(self) -> int:
        """Eliminar todo el historial."""
        count = len(self._history)
        self._history.clear()
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del historial."""
        if not self._history:
            return {"total_queries": 0, "average_results": 0, "most_common_entities": [], "recent_activity": False}
        
        total_queries = len(self._history)
        average_results = sum(item.search_results_count for item in self._history) / total_queries
        
        # Contar entidades más comunes
        entity_counts = {}
        for item in self._history:
            for entity_type, entities in item.entities.items():
                if isinstance(entities, list):
                    for entity in entities:
                        entity_counts[entity] = entity_counts.get(entity, 0) + 1     
        most_common_entities = sorted(
            entity_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Verificar actividad reciente (últimas 24 horas)
        recent_cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_activity = any(
            item.timestamp >= recent_cutoff 
            for item in self._history
        )
        
        return {
            "total_queries": total_queries,
            "average_results": round(average_results, 2),
            "most_common_entities": [{"entity": entity, "count": count} for entity, count in most_common_entities],
            "recent_activity": recent_activity
        } 