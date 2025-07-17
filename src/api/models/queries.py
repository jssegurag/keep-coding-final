from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    query: str = Field(..., description="Consulta del usuario", min_length=1, max_length=200)
    n_results: int = Field(10, description="Número de resultados a buscar", ge=1, le=50)

class QueryResponse(BaseModel):
    query: str
    response: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    filters_used: Dict[str, Any] = Field(default_factory=dict)
    search_results_count: int
    source_info: Dict[str, Any]
    enriched_metadata: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime

class BatchQueryRequest(BaseModel):
    queries: List[QueryRequest] = Field(..., description="Lista de consultas", min_items=1, max_items=10)

class BatchQueryResponse(BaseModel):
    results: List[QueryResponse]
    total_queries: int
    successful_queries: int
    failed_queries: int
    processing_time: float

# Modelos para historial de consultas
class QueryHistoryItem(BaseModel):
    id: str
    query: str
    response: str
    timestamp: datetime
    search_results_count: int
    source_info: Dict[str, Any]
    entities: Dict[str, Any] = Field(default_factory=dict)
    filters_used: Dict[str, Any] = Field(default_factory=dict)

class QueryHistoryResponse(BaseModel):
    queries: List[QueryHistoryItem]
    total_count: int
    page: int
    page_size: int
    total_pages: int

# Modelos para metadatos de documentos
class DocumentMetadata(BaseModel):
    document_id: str
    title: Optional[str] = None
    document_type: Optional[str] = None
    court: Optional[str] = None
    date_filed: Optional[datetime] = None
    case_number: Optional[str] = None
    parties: List[str] = Field(default_factory=list)
    legal_terms: List[str] = Field(default_factory=list)
    chunk_count: int
    total_length: int
    last_updated: datetime

class DocumentMetadataResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_count: int
    available_filters: Dict[str, List[str]]

# Modelos para filtros disponibles
class FilterOption(BaseModel):
    name: str
    display_name: str
    type: str  #text,select,date", "number"
    options: List[str] = Field(default_factory=list)
    description: Optional[str] = None

class AvailableFiltersResponse(BaseModel):
    filters: List[FilterOption]
    total_filters: int 