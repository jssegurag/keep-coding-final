from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from ..models.queries import DocumentMetadataResponse, DocumentMetadata
from ..services.metadata_service import MetadataService

router = APIRouter(prefix="/api/v1/metadata", tags=["Metadatos"])

def get_metadata_service() -> MetadataService:
    """Dependency injection para el servicio de metadatos."""
    return MetadataService()

@router.get("/documents", 
    response_model=DocumentMetadataResponse,
    summary="Listar Metadatos de Documentos",
    description="""
    # 📚 Metadatos de Documentos
    
    Este endpoint proporciona acceso a los metadatos de todos los documentos legales en el sistema.
    
    ## Características
    
    - **Paginación**: Navegación eficiente a través de grandes volúmenes de documentos
    - **Filtros Avanzados**: Filtrado por tipo de documento, tribunal, fechas, etc.
    - **Ordenamiento**: Múltiples criterios de ordenamiento disponibles
    - **Enriquecimiento**: Metadatos enriquecidos con entidades extraídas
    - **Filtros Disponibles**: Información sobre filtros aplicables
    
    ## Filtros Disponibles
    
    ### Por Tipo de Documento
    - **Sentencia**: Decisiones judiciales finales
    - **Demanda**: Documentos de inicio de proceso
    - **Recurso**: Apelaciones y recursos
    - **Auto**: Decisiones interlocutorias
    - **Acuerdo**: Acuerdos entre partes
    
    ### Por Tribunal
    - **Juzgado Civil**: Procesos civiles
    - **Juzgado Penal**: Procesos penales
    - **Juzgado Mercantil**: Procesos mercantiles
    - **Juzgado Laboral**: Procesos laborales
    - **Juzgado Familiar**: Procesos familiares
    
    ## Metadatos Incluidos
    
    Para cada documento se incluye:
    - Información básica (ID, título, tipo, tribunal)
    - Fechas de presentación y actualización
    - Partes involucradas (demandante, demandado, etc.)
    - Términos legales identificados
    - Estadísticas del documento (longitud, fragmentos)
    
    ## Ordenamiento
    
    Por defecto se ordena por fecha de presentación (más recientes primero).
    
    ## Límites
    
    - **Página máxima**: 1000 páginas
    - **Tamaño de página**: 1-50 documentos por página
    - **Filtros simultáneos**: Máximo 5 filtros activos
    """,
    responses={
        200: {
            "description": "Metadatos obtenidos exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "documents": [
                            {
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
                        ],
                        "total_count": 100,
                        "available_filters": {
                            "document_type": ["Sentencia", "Demanda", "Recurso"],
                            "court": ["Juzgado Civil", "Juzgado Penal"]
                        }
                    }
                }
            }
        },
        400: {
            "description": "Error en los parámetros de consulta",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "El número de página debe ser mayor a 0"
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en los parámetros",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["query", "page_size"],
                                "msg": "ensure this value is less than or equal to 50",
                                "type": "value_error.number.not_le"
                            }
                        ]
                    }
                }
            }
        }
    })
async def get_documents_metadata(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Tamaño de página"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    court: Optional[str] = Query(None, description="Filtrar por tribunal"),
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> DocumentMetadataResponse:
    """
    Obtiene metadatos de documentos con paginación y filtros.
    
    ## Parámetros de Consulta
    
    - **page**: Número de página (mínimo 1)
    - **page_size**: Tamaño de página (1-50 documentos)
    - **document_type**: Filtro opcional por tipo de documento
    - **court**: Filtro opcional por tribunal
    
    ## Respuesta
    
    Retorna una lista paginada de documentos con:
    - Metadatos completos de cada documento
    - Información de paginación
    - Filtros disponibles para refinar la búsqueda
    
    ## Ejemplo de Uso
    
    ```bash
    # Obtener primera página de sentencias
    curl "http://localhost:8001/api/v1/metadata/documents?page=1&page_size=10&document_type=Sentencia"
    
    # Filtrar por tribunal específico
    curl "http://localhost:8001/api/v1/metadata/documents?court=Juzgado Civil"
    
    # Combinar filtros
    curl "http://localhost:8001/api/v1/metadata/documents?document_type=Sentencia&court=Juzgado Civil"
    ```
    
    ## Filtros Futuros
    
    En próximas versiones se agregarán filtros por:
    - Rango de fechas
    - Número de expediente
    - Partes involucradas
    - Términos legales
    - Longitud del documento
    """
    try:
        return metadata_service.get_documents_metadata(
            page=page,
            page_size=page_size,
            document_type=document_type,
            court=court
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo metadatos: {str(e)}")

@router.get("/documents/{document_id}", 
    response_model=DocumentMetadata,
    summary="Obtener Metadatos de Documento Específico",
    description="""
    # 📄 Metadatos de Documento Específico
    
    Este endpoint proporciona metadatos detallados de un documento legal específico.
    
    ## Características
    
    - **Metadatos Completos**: Toda la información descriptiva del documento
    - **Entidades Extraídas**: Personas, organizaciones, fechas identificadas
    - **Términos Legales**: Vocabulario legal específico encontrado
    - **Estadísticas**: Métricas del documento (longitud, fragmentos)
    - **Partes Involucradas**: Demandante, demandado, abogados, etc.
    
    ## Información Incluida
    
    - **Datos Básicos**: ID, título, tipo, tribunal, número de expediente
    - **Fechas**: Presentación, emisión, última actualización
    - **Partes**: Demandante, demandado, representantes legales
    - **Términos Legales**: Vocabulario específico del derecho
    - **Estadísticas**: Longitud, número de fragmentos, complejidad
    
    ## Procesamiento
    
    El sistema realiza:
    1. **Extracción de Entidades**: Identifica personas, organizaciones, fechas
    2. **Análisis de Términos**: Detecta vocabulario legal específico
    3. **Identificación de Partes**: Determina roles en el proceso
    4. **Cálculo de Estadísticas**: Métricas de complejidad y estructura
    
    ## Casos de Uso
    
    - Análisis detallado de un documento específico
    - Extracción de información para reportes
    - Validación de metadatos
    - Análisis de complejidad documental
    """,
    responses={
        200: {
            "description": "Metadatos del documento obtenidos exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "DOC001",
                        "title": "Sentencia Civil - Juan Pérez vs María García",
                        "document_type": "Sentencia",
                        "court": "Juzgado Civil",
                        "date_filed": "2024-01-15T00:00:00Z",
                        "case_number": "CIV-2024-001",
                        "parties": ["Demandante", "Demandado"],
                        "legal_terms": ["demandante", "sentencia", "tribunal", "medida cautelar"],
                        "chunk_count": 5,
                        "total_length": 15000,
                        "last_updated": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Documento no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Documento no encontrado"
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error obteniendo documento: Error interno del servidor"
                    }
                }
            }
        }
    })
async def get_document_metadata(
    document_id: str,
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> DocumentMetadata:
    """
    Obtiene metadatos detallados de un documento específico.
    
    ## Parámetros
    
    - **document_id**: Identificador único del documento
    
    ## Respuesta
    
    Retorna metadatos completos del documento incluyendo:
    - Información básica del documento
    - Entidades extraídas (personas, organizaciones)
    - Términos legales identificados
    - Partes involucradas en el proceso
    - Estadísticas del documento
    
    ## Ejemplo de Uso
    
    ```bash
    curl "http://localhost:8001/api/v1/metadata/documents/DOC001"
    ```
    
    ## Información Adicional
    
    Los metadatos se actualizan automáticamente cuando:
    - Se procesa el documento por primera vez
    - Se detectan nuevas entidades
    - Se actualiza la información del expediente
    """
    try:
        document = metadata_service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo documento: {str(e)}")

@router.get("/documents/{document_id}/summary",
    summary="Obtener Resumen de Documento",
    description="""
    # 📋 Resumen de Documento
    
    Este endpoint proporciona un resumen ejecutivo de un documento legal específico.
    
    ## Características
    
    - **Resumen Ejecutivo**: Información clave del documento
    - **Estadísticas**: Métricas de complejidad y estructura
    - **Información Condensada**: Datos esenciales para análisis rápido
    - **Métricas de Análisis**: Conteos y estadísticas del documento
    
    ## Información Incluida
    
    - **Datos Básicos**: ID, título, tipo, tribunal, número de expediente
    - **Estadísticas**: Número de partes, términos legales, fragmentos
    - **Métricas**: Longitud total, complejidad, densidad de información
    - **Fechas**: Presentación y última actualización
    
    ## Casos de Uso
    
    - Análisis rápido de documentos
    - Generación de reportes ejecutivos
    - Comparación de documentos
    - Evaluación de complejidad
    - Selección de documentos para análisis detallado
    
    ## Diferencias con Metadatos Completos
    
    Este endpoint proporciona un resumen ejecutivo, mientras que el endpoint de metadatos
    incluye información detallada como entidades específicas y términos legales completos.
    """,
    responses={
        200: {
            "description": "Resumen del documento obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "DOC001",
                        "title": "Sentencia Civil - Juan Pérez vs María García",
                        "document_type": "Sentencia",
                        "court": "Juzgado Civil",
                        "case_number": "CIV-2024-001",
                        "parties_count": 2,
                        "legal_terms_count": 15,
                        "chunk_count": 5,
                        "total_length": 15000,
                        "last_updated": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Documento no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Documento no encontrado"
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error obteniendo resumen: Error interno del servidor"
                    }
                }
            }
        }
    })
async def get_document_summary(
    document_id: str,
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> dict:
    """
    Obtiene un resumen ejecutivo de un documento específico.
    
    ## Parámetros
    
    - **document_id**: Identificador único del documento
    
    ## Respuesta
    
    Retorna un resumen ejecutivo con:
    - Información básica del documento
    - Estadísticas de complejidad
    - Métricas de análisis
    - Conteos de elementos importantes
    
    ## Ejemplo de Uso
    
    ```bash
    curl "http://localhost:8001/api/v1/metadata/documents/DOC001/summary"
    ```
    
    ## Métricas Incluidas
    
    - **parties_count**: Número de partes involucradas
    - **legal_terms_count**: Número de términos legales identificados
    - **chunk_count**: Número de fragmentos del documento
    - **total_length**: Longitud total en caracteres
    
    ## Análisis de Complejidad
    
    El sistema calcula automáticamente:
    - Densidad de términos legales
    - Complejidad del lenguaje
    - Estructura del documento
    - Nivel de detalle
    """
    try:
        document = metadata_service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        return {
            "document_id": document.document_id,
            "title": document.title,
            "document_type": document.document_type,
            "court": document.court,
            "case_number": document.case_number,
            "parties_count": len(document.parties),
            "legal_terms_count": len(document.legal_terms),
            "chunk_count": document.chunk_count,
            "total_length": document.total_length,
            "last_updated": document.last_updated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}") 