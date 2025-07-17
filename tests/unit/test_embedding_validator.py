"""
Tests unitarios para el validador de embeddings
Siguiendo principios SOLID y GRASP
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.testing.embedding_validator import EmbeddingValidator

class TestEmbeddingValidator:
    """
    Tests unitarios para EmbeddingValidator.
    Responsabilidad única: Validar el comportamiento del validador.
    """
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.validator = EmbeddingValidator()
    
    def test_extract_filename_from_path(self):
        """Test de extracción de nombre de archivo del path"""
        # Test con path completo
        path = "idp/2025/7/15/1752614131.584725/app/DavExtraccion/PDFs/documents_20250715/Bogota2/RCCI2150725310.pdf"
        filename = self.validator._extract_filename_from_path(path)
        assert filename == "RCCI2150725310"
        
        # Test con path simple
        path_simple = "RCCI2150725310.pdf"
        filename_simple = self.validator._extract_filename_from_path(path_simple)
        assert filename_simple == "RCCI2150725310"
    
    def test_extract_text_from_docling(self):
        """Test de extracción de texto de estructura DoclingDocument"""
        # Mock de estructura DoclingDocument
        docling_content = {
            "texts": [
                {"text": "Alcaldía de"},
                {"text": "Bogotá"},
                {"text": "Resolución número 123"}
            ]
        }
        
        text = self.validator._extract_text_from_docling(docling_content)
        assert text == "Alcaldía de Bogotá Resolución número 123"
        
        # Test con estructura vacía
        empty_content = {"texts": []}
        empty_text = self.validator._extract_text_from_docling(empty_content)
        assert empty_text == ""
        
        # Test con estructura inválida
        invalid_content = {"other_field": "value"}
        invalid_text = self.validator._extract_text_from_docling(invalid_content)
        assert invalid_text == ""
    
    def test_extract_metadata_from_response(self):
        """Test de extracción de metadatos del JSON anidado"""
        # Test con persona física
        response_person = '{"demandante": {"nombresPersonaDemandante": "JUAN", "apellidosPersonaDemandante": "PÉREZ"}}'
        metadata = self.validator._extract_metadata_from_response(response_person)
        assert metadata['demandante'] == "JUAN PÉREZ"
        
        # Test con empresa
        response_company = '{"demandante": {"NombreEmpresaDemandante": "EMPRESA ABC S.A."}}'
        metadata_company = self.validator._extract_metadata_from_response(response_company)
        assert metadata_company['demandante'] == "EMPRESA ABC S.A."
        
        # Test con lista
        response_list = '[{"demandante": {"nombresPersonaDemandante": "MARÍA", "apellidosPersonaDemandante": "GARCÍA"}}]'
        metadata_list = self.validator._extract_metadata_from_response(response_list)
        assert metadata_list['demandante'] == "MARÍA GARCÍA"
        
        # Test con datos incompletos
        response_incomplete = '{"demandante": {}}'
        metadata_incomplete = self.validator._extract_metadata_from_response(response_incomplete)
        assert metadata_incomplete['demandante'] == "No especificado"
    
    def test_create_test_chunks(self):
        """Test de creación de chunks"""
        # Test con texto corto
        short_text = "Texto corto"
        chunks_short = self.validator._create_test_chunks(short_text, chunk_size=100, overlap=20)
        assert len(chunks_short) == 1
        assert chunks_short[0] == short_text
        
        # Test con texto largo
        long_text = "Este es un texto de prueba " * 100  # Texto largo
        chunks_long = self.validator._create_test_chunks(long_text, chunk_size=100, overlap=20)
        
        assert len(chunks_long) > 1
        assert all(len(chunk) <= 100 for chunk in chunks_long)
        
        # Verificar overlap
        for i in range(len(chunks_long) - 1):
            overlap_text = chunks_long[i][-20:]  # Últimos 20 caracteres
            assert overlap_text in chunks_long[i + 1]
    
    @patch('src.testing.embedding_validator.SentenceTransformer')
    def test_generate_embeddings(self, mock_sentence_transformer):
        """Test de generación de embeddings"""
        # Mock del modelo
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_sentence_transformer.return_value = mock_model
        
        # Crear nuevo validador con mock
        validator = EmbeddingValidator()
        
        texts = ["texto de prueba 1", "texto de prueba 2"]
        embeddings = validator.generate_embeddings(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 3)
        mock_model.encode.assert_called_once_with(texts)
    
    def test_create_test_questions(self):
        """Test de creación de preguntas de prueba"""
        questions = self.validator.create_test_questions()
        
        assert len(questions) == 10
        assert all(isinstance(q, tuple) and len(q) == 2 for q in questions)
        assert all(isinstance(q[0], str) and isinstance(q[1], str) for q in questions)
        
        # Verificar que las preguntas contienen palabras clave esperadas
        question_texts = [q[0] for q in questions]
        expected_keywords = ["demandante", "demandado", "cuantía", "medida", "fecha"]
        for keyword in expected_keywords:
            assert any(keyword in q for q in question_texts)
    
    def test_semantic_similarity_with_mock_documents(self):
        """Test de similitud semántica con documentos mock"""
        # Crear documentos de prueba
        self.validator.test_documents = [
            {
                'documentname': 'test1.pdf',
                'chunks': ['demandante Juan Pérez', 'demandado Empresa ABC'],
                'demandante': 'Juan Pérez'
            }
        ]
        
        # Mock del método generate_embeddings
        with patch.object(self.validator, 'generate_embeddings') as mock_generate:
            # Simular embeddings
            mock_generate.side_effect = [
                np.array([[0.1, 0.2], [0.3, 0.4]]),  # chunks
                np.array([[0.5, 0.6], [0.7, 0.8], [0.9, 1.0], [1.1, 1.2]])  # queries
            ]
            
            results = self.validator.test_semantic_similarity()
            
            assert 'test1.pdf' in results
            assert isinstance(results['test1.pdf'], float)
            assert 0 <= results['test1.pdf'] <= 1
    
    def test_name_search_with_mock_documents(self):
        """Test de búsqueda por nombres con documentos mock"""
        self.validator.test_documents = [
            {
                'documentname': 'test1.pdf',
                'chunks': ['demandante Juan Pérez', 'demandado Empresa ABC'],
                'demandante': 'Juan Pérez'
            }
        ]
        
        # Mock del método generate_embeddings
        with patch.object(self.validator, 'generate_embeddings') as mock_generate:
            # Simular embeddings
            mock_generate.side_effect = [
                np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]),  # names
                np.array([[0.9, 1.0], [1.1, 1.2]])  # chunks
            ]
            
            results = self.validator.test_name_search()
            
            assert 'test1.pdf' in results
            assert isinstance(results['test1.pdf'], float)
            assert 0 <= results['test1.pdf'] <= 1
    
    def test_legal_concepts_with_mock_documents(self):
        """Test de conceptos jurídicos con documentos mock"""
        self.validator.test_documents = [
            {
                'documentname': 'test1.pdf',
                'chunks': ['embargo preventivo', 'medida cautelar']
            }
        ]
        
        # Mock del método generate_embeddings
        with patch.object(self.validator, 'generate_embeddings') as mock_generate:
            # Simular embeddings
            mock_generate.side_effect = [
                np.array([[0.1, 0.2], [0.3, 0.4]]),  # concepts
                np.array([[0.5, 0.6], [0.7, 0.8]])  # chunks
            ]
            
            results = self.validator.test_legal_concepts()
            
            assert 'test1.pdf' in results
            assert isinstance(results['test1.pdf'], float)
            assert 0 <= results['test1.pdf'] <= 1
    
    def test_run_validation_with_error(self):
        """Test de validación con error"""
        # Mock load_test_documents para retornar lista vacía
        with patch.object(self.validator, 'load_test_documents', return_value=[]):
            results = self.validator.run_validation()
            
            assert "error" in results
            assert "No se pudieron cargar documentos de prueba" in results["error"]
    
    def test_print_results_with_error(self):
        """Test de impresión de resultados con error"""
        results = {"error": "Error de prueba"}
        
        # Capturar output
        with patch('builtins.print') as mock_print:
            self.validator.print_results(results)
            mock_print.assert_called_with("Error en validación: Error de prueba")
    
    def test_print_results_with_success(self):
        """Test de impresión de resultados exitosos"""
        results = {
            "metrics": {
                "avg_semantic_similarity": 0.8,
                "avg_name_search": 0.7,
                "avg_legal_concepts": 0.9,
                "overall_score": 0.8
            }
        }
        
        # Capturar output
        with patch('builtins.print') as mock_print:
            self.validator.print_results(results)
            
            # Verificar que se imprimieron las métricas
            calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Similitud Semántica Promedio: 0.800" in str(call) for call in calls)
            assert any("Embeddings validados - Apto para producción" in str(call) for call in calls) 