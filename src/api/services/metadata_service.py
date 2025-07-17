from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import os
from ..models.queries import DocumentMetadata, DocumentMetadataResponse

class MetadataService:
    def __init__(self):
        self.csv_path = "data/processed/legal_documents.csv"
        self._metadata_cache = None
    
    def _load_metadata(self) -> pd.DataFrame:
        """Cargar metadatos desde el CSV."""
        if self._metadata_cache is None:
            if os.path.exists(self.csv_path):
                try:
                    self._metadata_cache = pd.read_csv(self.csv_path)
                except Exception:
                    self._metadata_cache = pd.DataFrame()
            else:
                self._metadata_cache = pd.DataFrame()
        return self._metadata_cache
    
    def get_documents_metadata(self, page: int = 1, page_size: int = 10, 
                             document_type: Optional[str] = None,
                             court: Optional[str] = None) -> DocumentMetadataResponse:
        """Obtener metadatos de documentos con filtros."""
        df = self._load_metadata()
        
        if df.empty:
            return DocumentMetadataResponse(
                documents=[],
                total_count=0,
                available_filters={}
            )
        
        # Aplicar filtros
        if document_type:
            df = df[df['document_type'].notnull() & (df['document_type'].astype(str).str.lower() == document_type.lower())]
        if court:
            df = df[df['court'].str.contains(court, case=False)]
        
        # Calcular paginación
        total_count = len(df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Obtener página actual
        page_df = df.iloc[start_idx:end_idx]
        
        # Convertir a DocumentMetadata
        documents = []
        for _, row in page_df.iterrows():
            # Extraer términos legales del texto
            legal_terms = self._extract_legal_terms(row.get('content', ''))
            # Extraer partes del texto
            parties = self._extract_parties(row.get('content', ''))
            document = DocumentMetadata(
                document_id=row.get('document_id', ''),
                title=row.get('title', ''),
                document_type=row.get('document_type', ''),
                court=row.get('court', ''),
                date_filed=self._parse_date(row.get('date_filed')),
                case_number=row.get('case_number', ''),
                parties=parties,
                legal_terms=legal_terms,
                chunk_count=self._get_chunk_count(row.get('document_id', '')),
                total_length=len(str(row.get('content', ''))),
                last_updated=datetime.now()
            )
            documents.append(document)
        
        # Obtener filtros disponibles
        available_filters = self._get_available_filters()
        
        return DocumentMetadataResponse(
            documents=documents,
            total_count=total_count,
            available_filters=available_filters
        )
    
    def get_document_by_id(self, document_id: str) -> Optional[DocumentMetadata]:
        """Obtener metadatos de un documento específico."""
        df = self._load_metadata()
        
        if df.empty:
            return None
        
        doc_row = df[df['document_id'] == document_id]
        if doc_row.empty:
            return None
        
        row = doc_row.iloc[0]
        legal_terms = self._extract_legal_terms(row.get('content', ''))
        parties = self._extract_parties(row.get('content', ''))
        
        return DocumentMetadata(
            document_id=row.get('document_id', ''),
            title=row.get('title', ''),
            document_type=row.get('document_type', ''),
            court=row.get('court', ''),
            date_filed=self._parse_date(row.get('date_filed')),
            case_number=row.get('case_number', ''),
            parties=parties,
            legal_terms=legal_terms,
            chunk_count=self._get_chunk_count(row.get('document_id', '')),
            total_length=len(str(row.get('content', ''))),
            last_updated=datetime.now()
        )
    
    def _extract_legal_terms(self, text: str) -> List[str]:
        """Extraer términos legales del texto."""
        legal_terms = [
            'demandante', 'demandado', 'juez', 'tribunal', 'sentencia',
            'embargo', 'medida cautelar', 'recurso', 'apelación',
            'prueba', 'testigo', 'abogado', 'procurador', 'notario',
            'acta', 'expediente', 'proceso', 'litigio', 'controversia'
        ]
        
        found_terms = []
        text_lower = text.lower()
        for term in legal_terms:
            if term in text_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extraer partes del texto."""
        # Buscar patrones comunes de partes
        parties = []
        text_lower = text.lower()
        
        # Buscar demandante/demandado
        if 'demandante' in text_lower:
            parties.append('Demandante')
        if 'demandado' in text_lower:
            parties.append('Demandado')
        
        return parties
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parsear fecha de string a datetime."""
        if pd.isna(date_str) or not date_str:
            return None
        
        try:
            return pd.to_datetime(date_str)
        except:
            return None
    
    def _get_chunk_count(self, document_id: str) -> int:
        """Obtener número de chunks para un documento."""
        # Por simplicidad, asumimos 1 chunk por documento
        # En implementación real, consultaría la base de datos de embeddings
        return 1
    
    def _get_available_filters(self) -> Dict[str, List[str]]:
        """Filtros disponibles."""
        df = self._load_metadata()
        
        if df.empty:
            return {}
        
        filters = {}
        
        # Tipos de documento
        if 'document_type' in df.columns:
            filters['document_type'] = df['document_type'].dropna().unique().tolist()
        
        # Tribunales
        if 'court' in df.columns:
            filters['court'] = df['court'].dropna().unique().tolist()
        
        return filters 