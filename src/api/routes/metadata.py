from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from ..models.queries import DocumentMetadataResponse, DocumentMetadata
from ..services.metadata_service import MetadataService

router = APIRouter(prefix="/api/v1/metadata", tags=["Metadatos"])

def get_metadata_service() -> MetadataService:
    return MetadataService()

@router.get("/documents", response_model=DocumentMetadataResponse)
async def get_documents_metadata(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Tamaño de página"),
    document_type: Optional[str] = Query(None, description="Filtrar por tipo de documento"),
    court: Optional[str] = Query(None, description="Filtrar por tribunal"),
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> DocumentMetadataResponse:
    """Obtener metadatos de documentos con paginación y filtros."""
    try:
        return metadata_service.get_documents_metadata(
            page=page,
            page_size=page_size,
            document_type=document_type,
            court=court
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo metadatos: {str(e)}")

@router.get("/documents/{document_id}", response_model=DocumentMetadata)
async def get_document_metadata(
    document_id: str,
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> DocumentMetadata:
    """Obtener metadatos de un documento específico."""
    try:
        document = metadata_service.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo documento: {str(e)}")

@router.get("/documents/{document_id}/summary")
async def get_document_summary(
    document_id: str,
    metadata_service: MetadataService = Depends(get_metadata_service)
) -> dict:
    """Obtener resumen de un documento específico."""
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