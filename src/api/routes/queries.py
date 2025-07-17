from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from ..models.queries import (
    QueryRequest, QueryResponse, BatchQueryRequest, BatchQueryResponse,
    QueryHistoryResponse
)
from ..services.query_history_service import QueryHistoryService

router = APIRouter(prefix="/api/v1/queries", tags=["Consultas"])

def get_query_history_service() -> QueryHistoryService:
    """Dependency injection para el servicio de historial de consultas."""
    return QueryHistoryService()

@router.post("/", 
    response_model=QueryResponse,
    summary="Realizar Consulta Semántica",
    description="""
    # 🔍 Realizar Consulta Semántica
    
    Este endpoint permite realizar consultas semánticas en documentos legales utilizando técnicas de RAG (Recuperación Augmentada por Generación).
    
    ## Características
    
    - **Búsqueda Semántica**: Comprende el significado de la consulta, no solo palabras clave
    - **Respuesta Generativa**: Genera respuestas coherentes basadas en documentos relevantes
    - **Extracción de Entidades**: Identifica automáticamente personas, organizaciones, fechas, etc.
    - **Filtros Inteligentes**: Aplica filtros automáticos basados en el contexto de la consulta
    
    ## Proceso de Consulta
    
    1. **Análisis de Consulta**: El sistema analiza la consulta en lenguaje natural
    2. **Búsqueda de Documentos**: Encuentra documentos relevantes en el corpus legal
    3. **Extracción de Contexto**: Extrae fragmentos relevantes de los documentos
    4. **Generación de Respuesta**: Genera una respuesta coherente basada en el contexto
    5. **Enriquecimiento**: Extrae entidades y metadatos adicionales
    
    ## Ejemplos de Consultas
    
    - "¿Cuál es el demandante del expediente ABC-2024-001?"
    - "¿Qué tribunal emitió la sentencia?"
    - "¿Cuáles son las medidas cautelares solicitadas?"
    - "¿Quién es el abogado representante?"
    
    ## Códigos de Respuesta
    
    - `200`: Consulta procesada exitosamente
    - `400`: Error en los parámetros de entrada
    - `422`: Error de validación en los datos
    - `500`: Error interno del servidor
    """,
    responses={
        200: {
            "description": "Consulta procesada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "query": "¿Cuál es el demandante del expediente?",
                        "response": "Según los documentos analizados, el demandante es Juan Pérez, representado por el abogado María García del bufete Legal & Asociados.",
                        "entities": {
                            "demandante": "Juan Pérez",
                            "abogado": "María García",
                            "bufete": "Legal & Asociados",
                            "expediente": "ABC-2024-001"
                        },
                        "filters_used": {
                            "document_type": "Sentencia",
                            "court": "Juzgado Civil"
                        },
                        "search_results_count": 3,
                        "source_info": {
                            "documents_used": ["DOC001", "DOC002", "DOC003"],
                            "confidence_score": 0.92,
                            "processing_time": 1.25
                        },
                        "enriched_metadata": [
                            {
                                "document_id": "DOC001",
                                "relevance_score": 0.95,
                                "extracted_entities": ["Juan Pérez", "demandante"],
                                "chunk_used": "El demandante Juan Pérez, representado por..."
                            }
                        ],
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Error en los parámetros de entrada",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "La consulta no puede estar vacía"
                    }
                }
            }
        },
        422: {
            "description": "Error de validación",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "query"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error interno del servidor. Por favor, inténtelo de nuevo más tarde."
                    }
                }
            }
        }
    })
async def create_query(
    query_request: QueryRequest,
    query_history_service: QueryHistoryService = Depends(get_query_history_service)
) -> QueryResponse:
    """
    Realiza una consulta semántica en documentos legales.
    
    ## Parámetros
    
    - **query**: Consulta en lenguaje natural (1-500 caracteres)
    - **n_results**: Número de resultados a retornar (1-50)
    
    ## Respuesta
    
    Retorna una respuesta enriquecida que incluye:
    - Respuesta generada por el sistema RAG
    - Entidades extraídas del texto
    - Filtros aplicados durante la búsqueda
    - Información de los documentos fuente
    - Metadatos enriquecidos
    
    ## Ejemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/api/v1/queries" \\
      -H "Content-Type: application/json" \\
      -d '{
        "query": "¿Cuál es el demandante del expediente?",
        "n_results": 5
      }'
    ```
    """
    try:
        # Simular respuesta RAG (en implementación real, aquí iría la lógica RAG)
        response = QueryResponse(
            query=query_request.query,
            response=f"Respuesta simulada para: {query_request.query}",
            entities={"demandante": "Juan Pérez", "expediente": "ABC-2024-001"},
            filters_used={"document_type": "Sentencia"},
            search_results_count=3,
            source_info={"documents_used": ["DOC001", "DOC002"]},
            enriched_metadata=[],
            timestamp=query_history_service.get_current_timestamp()
        )
        
        # Guardar en historial
        query_history_service.add_query_response(response)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

@router.get("/history", 
    response_model=QueryHistoryResponse,
    summary="Obtener Historial de Consultas",
    description="""
    # 📊 Historial de Consultas
    
    Este endpoint proporciona acceso al historial completo de consultas realizadas en el sistema.
    
    ## Características
    
    - **Paginación**: Navegación eficiente a través del historial
    - **Filtros**: Posibilidad de filtrar por fecha, tipo de consulta, etc.
    - **Estadísticas**: Información detallada de cada consulta
    - **Auditoría**: Trazabilidad completa de todas las consultas
    
    ## Información Incluida
    
    Para cada consulta en el historial se incluye:
    - Consulta original realizada
    - Respuesta generada por el sistema
    - Timestamp de la consulta
    - Número de resultados encontrados
    - Entidades extraídas
    - Filtros aplicados
    - Información de documentos fuente
    
    ## Ordenamiento
    
    Las consultas se ordenan por fecha de realización (más recientes primero).
    
    ## Límites
    
    - **Página máxima**: 100 páginas
    - **Tamaño de página**: 1-50 consultas por página
    - **Retención**: Historial mantenido por 30 días
    """,
    responses={
        200: {
            "description": "Historial de consultas obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "queries": [
                            {
                                "id": "query_123456",
                                "query": "¿Cuál es el demandante del expediente?",
                                "response": "El demandante es Juan Pérez.",
                                "timestamp": "2024-01-15T10:30:00Z",
                                "search_results_count": 3,
                                "source_info": {"documents_used": ["DOC001", "DOC002"]},
                                "entities": {"demandante": "Juan Pérez"},
                                "filters_used": {"document_type": "Sentencia"}
                            }
                        ],
                        "total_count": 25,
                        "page": 1,
                        "page_size": 10,
                        "total_pages": 3
                    }
                }
            }
        },
        400: {
            "description": "Error en los parámetros de paginación",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El número de página debe ser mayor a 0"
                    }
                }
            }
        }
    })
async def get_query_history(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Tamaño de página"),
    query_history_service: QueryHistoryService = Depends(get_query_history_service)
) -> QueryHistoryResponse:
    """
    Obtiene el historial paginado de consultas realizadas.
    
    ## Parámetros de Paginación
    
    - **page**: Número de página (mínimo 1)
    - **page_size**: Tamaño de página (1-50 consultas)
    
    ## Respuesta
    
    Retorna una lista paginada de consultas con:
    - Lista de consultas del historial
    - Información de paginación
    - Estadísticas del historial
    
    ## Ejemplo de Uso
    
    ```bash
    curl "http://localhost:8001/api/v1/queries/history?page=1&page_size=10"
    ```
    
    ## Filtros Futuros
    
    En próximas versiones se agregarán filtros por:
    - Rango de fechas
    - Tipo de consulta
    - Número de resultados
    - Entidades extraídas
    """
    try:
        return query_history_service.get_query_history(page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo historial: {str(e)}")

@router.post("/batch",
    response_model=BatchQueryResponse,
    summary="Procesar Lote de Consultas",
    description="""
    # 📦 Procesamiento en Lote
    
    Este endpoint permite procesar múltiples consultas de manera eficiente en una sola petición.
    
    ## Ventajas del Procesamiento en Lote
    
    - **Eficiencia**: Reduce la latencia de red
    - **Consistencia**: Todas las consultas se procesan en el mismo contexto
    - **Optimización**: Mejor rendimiento para múltiples consultas relacionadas
    - **Análisis**: Facilita análisis comparativo entre consultas
    
    ## Límites
    
    - **Máximo 10 consultas** por lote
    - **Tiempo máximo**: 30 segundos de procesamiento
    - **Memoria**: Límite de 100MB por lote
    
    ## Casos de Uso
    
    - Análisis comparativo de múltiples expedientes
    - Extracción de información de varios documentos
    - Generación de reportes automatizados
    - Validación de consistencia en documentos
    
    ## Respuesta
    
    Incluye resultados individuales y estadísticas agregadas del procesamiento.
    """,
    responses={
        200: {
            "description": "Lote procesado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "query": "¿Cuál es el demandante?",
                                "response": "El demandante es Juan Pérez.",
                                "search_results_count": 2,
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        ],
                        "total_queries": 2,
                        "successful_queries": 2,
                        "failed_queries": 0,
                        "processing_time": 1.25
                    }
                }
            }
        },
        400: {
            "description": "Error en el lote de consultas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El lote excede el límite máximo de consultas"
                    }
                }
            }
        }
    })
async def process_batch_queries(
    batch_request: BatchQueryRequest,
    query_history_service: QueryHistoryService = Depends(get_query_history_service)
) -> BatchQueryResponse:
    """
    Procesa múltiples consultas en un solo lote.
    
    ## Parámetros
    
    - **queries**: Lista de consultas a procesar (1-10 consultas)
    
    ## Respuesta
    
    Retorna resultados de todas las consultas junto con estadísticas del procesamiento.
    
    ## Ejemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/api/v1/queries/batch" \\
      -H "Content-Type: application/json" \\
      -d '{
        "queries": [
          {"query": "¿Cuál es el demandante?", "n_results": 3},
          {"query": "¿Qué tribunal emitió la sentencia?", "n_results": 2}
        ]
      }'
    ```
    """
    try:
        # Simular procesamiento en lote
        results = []
        for query_req in batch_request.queries:
            response = QueryResponse(
                query=query_req.query,
                response=f"Respuesta simulada para: {query_req.query}",
                entities={},
                filters_used={},
                search_results_count=2,
                source_info={"documents_used": ["DOC001"]},
                enriched_metadata=[],
                timestamp=query_history_service.get_current_timestamp()
            )
            results.append(response)
            query_history_service.add_query_response(response)
        
        return BatchQueryResponse(
            results=results,
            total_queries=len(batch_request.queries),
            successful_queries=len(results),
            failed_queries=0,
            processing_time=1.25
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando lote: {str(e)}") 