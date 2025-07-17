"""
Tests de integración para el pipeline completo
"""
import pytest
import tempfile
import os
from src.testing.integration_tester import IntegrationTester

class TestFullPipeline:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.tester = IntegrationTester()
    
    def test_individual_components(self):
        """Test de componentes individuales"""
        results = self.tester._test_individual_components()
        
        # Verificar chunker
        assert results["chunker"]["success"] == True
        assert results["chunker"]["chunks_created"] > 0
        
        # Verificar indexer
        assert results["indexer"]["success"] == True
        
        # Verificar query handler
        assert results["query_handler"]["success"] == True
    
    def test_indexing(self):
        """Test de indexación"""
        results = self.tester._test_indexing()
        
        assert results["success"] == True
        assert results["has_data"] == True
    
    def test_search(self):
        """Test de búsqueda"""
        results = self.tester._test_search()
        
        assert results["success"] == True
        assert len(results["results"]) > 0
        
        for result in results["results"]:
            assert result["success"] == True
    
    def test_queries(self):
        """Test de consultas"""
        results = self.tester._test_queries()
        
        assert results["success"] == True
        assert len(results["results"]) > 0
        
        for result in results["results"]:
            assert result["success"] == True
            assert result["has_response"] == True
            assert result["has_source"] == True
    
    def test_complete_pipeline(self):
        """Test del pipeline completo"""
        results = self.tester._test_complete_pipeline()
        
        assert results["success"] == True
        assert results["has_response"] == True
        assert results["has_source"] == True
        assert results["response_time"] < 10  # Menos de 10 segundos
    
    def test_evaluation_questions(self):
        """Test de preguntas de evaluación"""
        questions = self.tester.evaluation_questions
        
        assert len(questions) == 20
        
        # Verificar categorías
        categories = [q["category"] for q in questions]
        assert "metadatos" in categories
        assert "contenido" in categories
        assert "resumen" in categories
        
        # Verificar tipos
        types = [q["type"] for q in questions]
        assert "extraction" in types
        assert "comprehension" in types
        assert "summary" in types
        
        # Verificar que hay preguntas con documentos reales
        real_docs = [q for q in questions if q.get("real_document")]
        assert len(real_docs) > 0
    
    def test_response_quality_evaluation(self):
        """Test de evaluación de calidad de respuesta"""
        # Respuesta excelente
        excellent_response = "El demandante es Juan Pérez. Fuente: test_doc, Chunk 1 de 3"
        question = {"expected_keywords": ["demandante", "Juan"], "type": "extraction"}
        
        score = self.tester._evaluate_response_quality(excellent_response, question)
        assert score >= 4
        
        # Respuesta pobre
        poor_response = "No se encuentra información"
        score = self.tester._evaluate_response_quality(poor_response, question)
        assert score <= 2
    
    def test_real_data_loading(self):
        """Test de carga de datos reales"""
        real_data = self.tester.real_data
        
        assert "documents" in real_data
        assert "total_available" in real_data
        assert real_data["total_available"] > 0
        
        # Verificar que hay documentos para testing
        documents = real_data.get("documents", [])
        assert len(documents) > 0
        
        # Verificar estructura de documentos
        for doc in documents[:3]:  # Verificar primeros 3
            assert "document_id" in doc
            assert "demandante" in doc
    
    def test_end_to_end_pipeline_integration(self):
        """Test de integración end-to-end completo"""
        results = self.tester.test_end_to_end_pipeline()
        
        # Verificar estructura de resultados
        assert "components" in results
        assert "indexing" in results
        assert "search" in results
        assert "queries" in results
        assert "pipeline" in results
        assert "errors" in results
        
        # Verificar que no hay errores críticos
        assert len(results["errors"]) == 0
        
        # Verificar que todos los componentes funcionan
        components = results["components"]
        assert components["chunker"]["success"] == True
        assert components["indexer"]["success"] == True
        assert components["query_handler"]["success"] == True
    
    def test_qualitative_evaluation(self):
        """Test de evaluación cualitativa"""
        results = self.tester.run_qualitative_evaluation()
        
        # Verificar estructura
        assert "questions" in results
        assert "summary" in results
        assert len(results["questions"]) == 20
        
        # Verificar estadísticas
        summary = results["summary"]
        assert "successful_questions" in summary
        assert "success_rate" in summary
        assert "average_quality" in summary
        assert "average_response_time" in summary
        
        # Verificar que hay preguntas exitosas
        assert summary["successful_questions"] > 0
        assert summary["success_rate"] > 0
        
        # Verificar distribución de calidad
        quality_dist = summary.get("quality_distribution", {})
        assert "excellent" in quality_dist
        assert "good" in quality_dist
        assert "acceptable" in quality_dist
        assert "poor" in quality_dist 