from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """
    Modelo para solicitar una consulta semántica en documentos legales.
    
    Este modelo define los parámetros necesarios para realizar una búsqueda
    semántica en el corpus de documentos legales utilizando técnicas RAG.
    """
    query: str = Field(
        ..., 
        description="Consulta del usuario en lenguaje natural",
        min_length=1, 
        max_length=2000,  # Aumentado de 500 a 2000 caracteres
        json_schema_extra={"example": "¿Cuál es el demandante del expediente ABC-2024-001?"}
    )
    n_results: int = Field(
        10, 
        description="Número de resultados a buscar y retornar",
        ge=1, 
        le=50,  # Máximo 50 resultados (ya estaba en 50)
        json_schema_extra={"example": 5}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cuál es el demandante del expediente ABC-2024-001? ¿Puede proporcionar información detallada sobre las partes involucradas, las fechas importantes del proceso, los montos reclamados y las medidas cautelares solicitadas? También necesito información sobre el tribunal competente y el estado actual del proceso.",
                "n_results": 10
            }
        }
    )

class QueryResponse(BaseModel):
    """
    Respuesta a una consulta semántica con información enriquecida.
    
    Incluye la respuesta generada, entidades extraídas, filtros aplicados
    y metadatos de los documentos fuente utilizados.
    """
    query: str = Field(..., description="Consulta original del usuario")
    response: str = Field(..., description="Respuesta generada por el sistema RAG")
    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Entidades extraídas del texto (personas, organizaciones, fechas, etc.)"
    )
    filters_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filtros aplicados durante la búsqueda"
    )
    search_results_count: int = Field(..., description="Número de documentos encontrados")
    source_info: Dict[str, Any] = Field(
        ..., 
        description="Información de los documentos fuente utilizados"
    )
    enriched_metadata: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Metadatos enriquecidos de los documentos fuente"
    )
    search_strategy: str = Field(
        default="semantic",
        description="Estrategia de búsqueda utilizada (semantic, document_id_exact, etc.)"
    )
    search_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Resultados completos de la búsqueda semántica (chunks, metadatos, distancias)"
    )
    timestamp: datetime = Field(..., description="Timestamp de cuando se realizó la consulta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cuál es el demandante del expediente?",
                "response": "Según los documentos analizados, el demandante es Juan Pérez, representado por el abogado María García.",
                "entities": {
                    "demandante": "Juan Pérez",
                    "abogado": "María García",
                    "expediente": "ABC-2024-001"
                },
                "filters_used": {
                    "document_type": "Sentencia",
                    "court": "Juzgado Civil"
                },
                "search_results_count": 3,
                "source_info": {
                    "documents_used": ["DOC001", "DOC002"],
                    "confidence_score": 0.85
                },
                "enriched_metadata": [
                    {
                        "document_id": "DOC001",
                        "relevance_score": 0.92,
                        "extracted_entities": ["Juan Pérez", "demandante"]
                    }
                ],
                "search_strategy": "semantic",
                "search_results": {
                    "documents": [["Contenido del chunk 1", "Contenido del chunk 2"]],
                    "metadatas": [[{"document_id": "DOC001", "chunk_id": "chunk_1"}, {"document_id": "DOC002", "chunk_id": "chunk_2"}]],
                    "distances": [[0.1, 0.3]],
                    "total_results": 2
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )

class BatchQueryRequest(BaseModel):
    """
    Modelo para realizar múltiples consultas en una sola petición.
    
    Permite procesar varias consultas de manera eficiente, útil para
    análisis comparativo o procesamiento en lote.
    """
    queries: List[QueryRequest] = Field(
        ..., 
        description="Lista de consultas a procesar",
        min_length=1, 
        max_length=10,
        json_schema_extra={
            "example": [
                {"query": "¿Cuál es el demandante?", "n_results": 3},
                {"query": "¿Qué tribunal emitió la sentencia?", "n_results": 2}
            ]
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "queries": [
                    {
                        "query": "¿Cuál es el demandante del expediente?",
                        "n_results": 3
                    },
                    {
                        "query": "¿Qué tribunal emitió la sentencia?",
                        "n_results": 2
                    }
                ]
            }
        }
    )

class BatchQueryResponse(BaseModel):
    """
    Respuesta a un lote de consultas con estadísticas de procesamiento.
    
    Incluye todos los resultados individuales junto con métricas
    de rendimiento y estadísticas del procesamiento.
    """
    results: List[QueryResponse] = Field(..., description="Resultados de todas las consultas")
    total_queries: int = Field(..., description="Número total de consultas procesadas")
    successful_queries: int = Field(..., description="Número de consultas exitosas")
    failed_queries: int = Field(..., description="Número de consultas que fallaron")
    processing_time: float = Field(..., description="Tiempo total de procesamiento en segundos")

    model_config = ConfigDict(
        json_schema_extra={
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
    )

# Modelos para historial de consultas
class QueryHistoryItem(BaseModel):
    """
    Elemento individual del historial de consultas.
    
    Representa una consulta realizada anteriormente con toda su
    información asociada para auditoría y análisis.
    """
    id: str = Field(..., description="Identificador único de la consulta")
    query: str = Field(..., description="Consulta original realizada")
    response: str = Field(..., description="Respuesta generada")
    timestamp: datetime = Field(..., description="Fecha y hora de la consulta")
    search_results_count: int = Field(..., description="Número de resultados encontrados")
    source_info: Dict[str, Any] = Field(
        ..., 
        description="Información de los documentos fuente utilizados"
    )
    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Entidades extraídas durante la consulta"
    )
    filters_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filtros aplicados en la consulta"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "query_123456",
                "query": "¿Cuál es el demandante?",
                "response": "El demandante es Juan Pérez.",
                "timestamp": "2024-01-15T10:30:00Z",
                "search_results_count": 3,
                "source_info": {"documents_used": ["DOC001", "DOC002"]},
                "entities": {"demandante": "Juan Pérez"},
                "filters_used": {"document_type": "Sentencia"}
            }
        }
    )

class QueryHistoryResponse(BaseModel):
    """
    Respuesta paginada del historial de consultas.
    
    Proporciona una lista paginada de consultas anteriores con
    información de paginación para navegación eficiente.
    """
    queries: List[QueryHistoryItem] = Field(..., description="Lista de consultas del historial")
    total_count: int = Field(..., description="Número total de consultas en el historial")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de la página")
    total_pages: int = Field(..., description="Número total de páginas")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "queries": [
                    {
                        "id": "query_123456",
                        "query": "¿Cuál es el demandante?",
                        "response": "El demandante es Juan Pérez.",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "search_results_count": 3
                    }
                ],
                "total_count": 25,
                "page": 1,
                "page_size": 10,
                "total_pages": 3
            }
        }
    )

# Modelos para metadatos de documentos
class DocumentMetadata(BaseModel):
    """
    Metadatos completos de un documento legal.
    
    Contiene toda la información descriptiva de un documento,
    incluyendo datos básicos, entidades extraídas y estadísticas.
    """
    document_id: str = Field(..., description="Identificador único del documento")
    title: Optional[str] = Field(None, description="Título del documento")
    document_type: Optional[str] = Field(None, description="Tipo de documento legal")
    court: Optional[str] = Field(None, description="Tribunal que emitió el documento")
    date_filed: Optional[datetime] = Field(None, description="Fecha de presentación del documento")
    case_number: Optional[str] = Field(None, description="Número de expediente")
    parties: List[str] = Field(
        default_factory=list,
        description="Partes involucradas en el documento (demandante, demandado, etc.)"
    )
    legal_terms: List[str] = Field(
        default_factory=list,
        description="Términos legales identificados en el documento"
    )
    chunk_count: int = Field(..., description="Número de fragmentos en que se dividió el documento")
    total_length: int = Field(..., description="Longitud total del documento en caracteres")
    last_updated: datetime = Field(..., description="Última actualización de los metadatos")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "DOC001",
                "title": "Sentencia Civil - Juan Pérez vs María García",
                "document_type": "Sentencia",
                "court": "Juzgado Civil",
                "date_filed": "2024-01-15T00:00:00Z",
                "case_number": "CIV-2024-001",
                "parties": ["Demandante", "Demandado"],
                "legal_terms": ["demandante", "sentencia", "tribunal"],
                "chunk_count": 5,
                "total_length": 15000,
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }
    )

class DocumentMetadataResponse(BaseModel):
    """
    Respuesta paginada de metadatos de documentos.
    
    Proporciona una lista paginada de documentos con sus metadatos
    y filtros disponibles para navegación eficiente.
    """
    documents: List[DocumentMetadata] = Field(..., description="Lista de documentos con sus metadatos")
    total_count: int = Field(..., description="Número total de documentos disponibles")
    available_filters: Dict[str, List[str]] = Field(
        ..., 
        description="Filtros disponibles para refinar la búsqueda"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "documents": [
                    {
                        "document_id": "DOC001",
                        "title": "Sentencia Civil",
                        "document_type": "Sentencia",
                        "court": "Juzgado Civil",
                        "chunk_count": 5,
                        "total_length": 15000
                    }
                ],
                "total_count": 100,
                "available_filters": {
                    "document_type": ["Sentencia", "Demanda", "Recurso"],
                    "court": ["Juzgado Civil", "Juzgado Penal"]
                }
            }
        }
    )

# Modelos para filtros disponibles
class FilterOption(BaseModel):
    """
    Opción de filtro disponible para refinar búsquedas.
    
    Define una opción de filtro con su nombre, tipo y valores
    posibles para facilitar la construcción de consultas.
    """
    name: str = Field(..., description="Nombre del filtro")
    display_name: str = Field(..., description="Nombre para mostrar en la interfaz")
    type: str = Field(..., description="Tipo de filtro (text, select, date, number)")
    options: List[str] = Field(
        default_factory=list,
        description="Opciones disponibles para el filtro"
    )
    description: Optional[str] = Field(None, description="Descripción del filtro")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "document_type",
                "display_name": "Tipo de Documento",
                "type": "select",
                "options": ["Sentencia", "Demanda", "Recurso"],
                "description": "Filtrar por tipo de documento legal"
            }
        }
    )

class AvailableFiltersResponse(BaseModel):
    """
    Respuesta con todos los filtros disponibles en el sistema.
    
    Proporciona una lista completa de filtros disponibles
    para ayudar a los usuarios a construir consultas efectivas.
    """
    filters: List[FilterOption] = Field(..., description="Lista de filtros disponibles")
    total_filters: int = Field(..., description="Número total de filtros disponibles")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filters": [
                    {
                        "name": "document_type",
                        "display_name": "Tipo de Documento",
                        "type": "select",
                        "options": ["Sentencia", "Demanda", "Recurso"]
                    },
                    {
                        "name": "court",
                        "display_name": "Tribunal",
                        "type": "select",
                        "options": ["Juzgado Civil", "Juzgado Penal"]
                    }
                ],
                "total_filters": 2
            }
        }
    ) 