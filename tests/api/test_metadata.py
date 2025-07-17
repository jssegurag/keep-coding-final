import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from src.api.main import app

client = TestClient(app)

class TestMetadataEndpoints:
    """Pruebas unitarias para endpoints de metadatos de documentos."""
    
    def setup_method(self):
        """Configuración inicial para cada prueba."""
        self.sample_document = {
            'document_id': 'DOC001',
            'title': 'Sentencia Civil',
            'document_type': 'Sentencia',
            'court': 'Juzgado Civil',
            'date_filed': '2024-01-15',
            'case_number': 'CIV-2024-001',
            'content': 'El demandante Juan Pérez solicita...'
        }
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_documents_metadata_success(self, mock_read_csv, mock_exists):
        """Prueba obtener metadatos de documentos exitosamente."""
        # Mock del DataFrame
        mock_df = pd.DataFrame([self.sample_document])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total_count" in data
        assert "available_filters" in data
        assert data["total_count"] == 1
        assert len(data["documents"]) == 1
        
        document = data["documents"][0]
        assert document["document_id"] == "DOC001"
        assert document["title"] == "Sentencia Civil"
        assert document["document_type"] == "Sentencia"
        assert document["court"] == "Juzgado Civil"
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_documents_metadata_empty(self, mock_read_csv, mock_exists):
        """Prueba obtener metadatos cuando no hay documentos."""
        # Mock de DataFrame vacío
        mock_read_csv.return_value = pd.DataFrame()
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []
        assert data["total_count"] == 0
        assert data["available_filters"] == {}
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_documents_metadata_with_pagination(self, mock_read_csv, mock_exists):
        """Prueba paginación de metadatos."""
        # Crear múltiples documentos
        documents = []
        for i in range(25):
            doc = self.sample_document.copy()
            doc['document_id'] = f'DOC{i:03d}'
            documents.append(doc)
        
        mock_df = pd.DataFrame(documents)
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        # Probar primera página
        response = client.get("/api/v1/metadata/documents?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 25
        assert len(data["documents"]) == 10
        
        # Probar segunda página
        response = client.get("/api/v1/metadata/documents?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["documents"]) == 10
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_documents_metadata_with_filters(self, mock_read_csv, mock_exists):
        """Prueba filtros de metadatos."""
        documents = [
            self.sample_document.copy(),
            {**self.sample_document, 'document_id': 'DOC002', 'document_type': 'Demanda'},
            {**self.sample_document, 'document_id': 'DOC003', 'court': 'Juzgado Penal'}
        ]
        mock_df = pd.DataFrame(documents)
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        # Filtrar por tipo de documento
        response = client.get("/api/v1/metadata/documents?document_type=Sentencia")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert all(doc["document_type"] == "Sentencia" for doc in data["documents"])
        
        # Filtrar por tribunal
        response = client.get("/api/v1/metadata/documents?court=Juzgado Civil")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_document_by_id_success(self, mock_read_csv, mock_exists):
        """Prueba obtener metadatos de un documento específico."""
        mock_df = pd.DataFrame([self.sample_document])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/DOC001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == "DOC001"
        assert data["title"] == "Sentencia Civil"
        assert data["document_type"] == "Sentencia"
        assert data["court"] == "Juzgado Civil"
        assert "parties" in data
        assert "legal_terms" in data
        assert "chunk_count" in data
        assert "total_length" in data
        assert "last_updated" in data
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_document_by_id_not_found(self, mock_read_csv, mock_exists):
        """Prueba obtener metadatos de documento inexistente."""
        mock_df = pd.DataFrame([self.sample_document])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/NONEXISTENT")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "no encontrado" in data["detail"].lower()
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_document_summary_success(self, mock_read_csv, mock_exists):
        """Prueba obtener resumen de documento."""
        mock_df = pd.DataFrame([self.sample_document])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/DOC001/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == "DOC001"
        assert data["title"] == "Sentencia Civil"
        assert data["document_type"] == "Sentencia"
        assert data["court"] == "Juzgado Civil"
        assert data["case_number"] == "CIV-2024-001"
        assert "parties_count" in data
        assert "legal_terms_count" in data
        assert "chunk_count" in data
        assert "total_length" in data
        assert "last_updated" in data
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_get_document_summary_not_found(self, mock_read_csv, mock_exists):
        """Prueba obtener resumen de documento inexistente."""
        mock_df = pd.DataFrame([self.sample_document])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/NONEXISTENT/summary")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "no encontrado" in data["detail"].lower()
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_available_filters(self, mock_read_csv, mock_exists):
        """Prueba que se devuelvan filtros disponibles."""
        documents = [
            {**self.sample_document, 'document_type': 'Sentencia'},
            {**self.sample_document, 'document_id': 'DOC002', 'document_type': 'Demanda'},
            {**self.sample_document, 'document_id': 'DOC003', 'court': 'Juzgado Penal'}
        ]
        mock_df = pd.DataFrame(documents)
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert "available_filters" in data
        filters = data["available_filters"]
        
        # Verificar que se incluyan los filtros esperados
        if "document_type" in filters:
            assert "Sentencia" in filters["document_type"]
            assert "Demanda" in filters["document_type"]
        
        if "court" in filters:
            assert "Juzgado Civil" in filters["court"]
            assert "Juzgado Penal" in filters["court"]
    
    def test_invalid_page_parameter(self):
        """Prueba parámetros de página inválidos."""
        response = client.get("/api/v1/metadata/documents?page=0")
        assert response.status_code == 422  # Validation error
        
        response = client.get("/api/v1/metadata/documents?page_size=0")
        assert response.status_code == 422
    
    def test_invalid_page_size_parameter(self):
        """Prueba tamaño de página inválido."""
        response = client.get("/api/v1/metadata/documents?page_size=100")
        assert response.status_code == 422  # Debería ser <= 50
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_legal_terms_extraction(self, mock_read_csv, mock_exists):
        """Prueba extracción de términos legales."""
        document_with_legal_terms = {
            **self.sample_document,
            'content': 'El demandante Juan Pérez solicita una medida cautelar. El juez del tribunal...'
        }
        mock_df = pd.DataFrame([document_with_legal_terms])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/DOC001")
        
        assert response.status_code == 200
        data = response.json()
        legal_terms = data["legal_terms"]
        
        # Verificar que se extraigan términos legales
        assert isinstance(legal_terms, list)
        # Al menos debería encontrar algunos términos del contenido
        assert len(legal_terms) > 0
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_parties_extraction(self, mock_read_csv, mock_exists):
        """Prueba extracción de partes."""
        document_with_parties = {
            **self.sample_document,
            'content': 'El demandante Juan Pérez demanda al demandado María García...'
        }
        mock_df = pd.DataFrame([document_with_parties])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/DOC001")
        
        assert response.status_code == 200
        data = response.json()
        parties = data["parties"]
        
        # Verificar que se extraigan las partes
        assert isinstance(parties, list)
        assert "Demandante" in parties
        assert "Demandado" in parties
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_date_parsing(self, mock_read_csv, mock_exists):
        """Prueba parsing de fechas."""
        document_with_date = {
            **self.sample_document,
            'date_filed': '2024-01-15'
        }
        mock_df = pd.DataFrame([document_with_date])
        mock_read_csv.return_value = mock_df
        mock_exists.return_value = True
        
        response = client.get("/api/v1/metadata/documents/DOC001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["date_filed"] is not None
        
        # Probar con fecha inválida
        document_invalid_date = {
            **self.sample_document,
            'date_filed': 'fecha-invalida'
        }
        mock_df = pd.DataFrame([document_invalid_date])
        mock_read_csv.return_value = mock_df
        
        response = client.get("/api/v1/metadata/documents/DOC001")
        assert response.status_code == 200
        data = response.json()
        assert data["date_filed"] is None

class TestMetadataServiceIntegration:
    """Pruebas de integración para el servicio de metadatos."""
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_csv_file_not_exists(self, mock_read_csv, mock_exists):
        """Prueba cuando el archivo CSV no existe."""
        mock_exists.return_value = False
        
        response = client.get("/api/v1/metadata/documents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []
        assert data["total_count"] == 0
    
    @patch('src.api.services.metadata_service.os.path.exists')
    @patch('src.api.services.metadata_service.pd.read_csv')
    def test_csv_reading_error(self, mock_read_csv, mock_exists):
        """Prueba manejo de errores al leer CSV."""
        mock_exists.return_value = True
        mock_read_csv.side_effect = Exception("Error reading CSV")
        
        response = client.get("/api/v1/metadata/documents")
        
        # El servicio debería manejar el error y devolver lista vacía
        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []
        assert data["total_count"] == 0 