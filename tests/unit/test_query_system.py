"""
Tests unitarios para el sistema de consultas orientados a documentos reales
"""
import pytest
from unittest.mock import Mock, patch
from src.query.query_handler import QueryHandler
from src.query.filter_extractor import FilterExtractor

class TestQueryHandler:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                self.query_handler = QueryHandler()
    
    def test_extract_entities_from_real_query(self):
        """Test de extracción de entidades de consulta real"""
        query = "tienes información de Coordinadora comercial de cargas CCC SA"
        entities = self.query_handler._extract_entities_from_query(query)
        
        assert 'names' in entities
        assert 'CCC SA' in entities['names']
    
    def test_extract_filters_for_structured_query(self):
        """Test de extracción de filtros para consultas estructuradas"""
        query = "¿Cuál es la cuantía de $1,000,000?"
        filters = self.query_handler._extract_filters_from_query(query)
        
        assert 'cuantia_normalized' in filters
        assert filters['cuantia_normalized'] == '1000000'
    
    def test_extract_filters_with_date(self):
        """Test de extracción de filtros con fecha"""
        query = "¿Cuál es la fecha del 15/01/2024?"
        filters = self.query_handler._extract_filters_from_query(query)
        
        assert 'fecha_normalized' in filters
        assert filters['fecha_normalized'] == '15/01/2024'
    
    def test_extract_filters_with_document_number(self):
        """Test de extracción de filtros con número de expediente"""
        query = "expediente numero RCCI2150725299"
        filters = self.query_handler._extract_filters_from_query(query)
        
        assert 'document_id' in filters
        assert filters['document_id'] == 'RCCI2150725299'
    
    def test_extract_filters_with_document_number_variations(self):
        """Test de extracción de filtros con variaciones de número de expediente"""
        queries = [
            "expediente RCCI2150725299",
            "documento RCCI2150725299",
            "caso RCCI2150725299",
            "RCCI2150725299"
        ]
        
        for query in queries:
            filters = self.query_handler._extract_filters_from_query(query)
            assert 'document_id' in filters
            assert filters['document_id'] == 'RCCI2150725299'
    
    def test_no_filters_for_general_queries(self):
        """Test de que no se extraen filtros para consultas generales"""
        query = "¿Qué información hay sobre embargos?"
        filters = self.query_handler._extract_filters_from_query(query)
        
        # No debería extraer filtros para consultas generales
        assert not filters or 'demandante_normalized' not in filters
    
    def test_format_context_for_real_documents(self):
        """Test de formateo de contexto con documentos reales"""
        search_results = {
            'results': {
                'documents': [['Texto del expediente RCCI2150725299 sobre Coordinadora comercial de cargas CCC SA']],
                'metadatas': [[{
                    'document_id': 'RCCI2150725299',
                    'chunk_position': 1,
                    'total_chunks': 2,
                    'demandante': 'COORDINADORA COMERCIAL DE CARGAS CCC SA',
                    'ciudad': 'Barranquilla'
                }]]
            }
        }
        
        context = self.query_handler._format_context_for_prompt(search_results)
        
        assert 'RCCI2150725299' in context
        assert 'Chunk 1/2' in context
        assert 'Coordinadora comercial' in context
    
    def test_extract_source_info_from_real_document(self):
        """Test de extracción de información de fuente de documento real"""
        search_results = {
            'results': {
                'metadatas': [[{
                    'document_id': 'RCCI2150725299',
                    'chunk_position': 2,
                    'total_chunks': 2,
                    'demandante': 'COORDINADORA COMERCIAL DE CARGAS CCC SA'
                }]]
            }
        }
        
        source_info = self.query_handler._extract_source_info(search_results)
        
        assert source_info['document_id'] == 'RCCI2150725299'
        assert source_info['chunk_position'] == 2
        assert source_info['total_chunks'] == 2
    
    def test_correlate_entities_with_metadata(self):
        """Test de correlación de entidades con metadatos reales"""
        entities = {'names': ['CCC SA']}
        search_results = {
            'results': {
                'metadatas': [[{
                    'demandante': 'COORDINADORA COMERCIAL DE CARGAS CCC SA',
                    'demandante_normalized': 'coordinadora comercial de cargas ccc sa',
                    'document_id': 'RCCI2150725299'
                }]]
            }
        }
        
        enriched = self.query_handler._correlate_entities_with_metadata(entities, search_results)
        
        assert len(enriched) > 0
        assert 'matches' in enriched[0]
        assert 'names' in enriched[0]['matches']
        assert any('CCC SA' in match['entity'] for match in enriched[0]['matches']['names'])

class TestFilterExtractor:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.extractor = FilterExtractor()
    
    def test_extract_demandante_from_real_name(self):
        """Test de extracción de demandante con nombre real"""
        query = "El demandante es COORDINADORA COMERCIAL DE CARGAS CCC SA"
        filters = self.extractor.extract_filters(query)
        
        assert 'demandante_normalized' in filters
        assert 'coordinadora comercial de cargas ccc sa' in filters['demandante_normalized']
    
    def test_extract_cuantia_from_real_amount(self):
        """Test de extracción de cuantía con monto real"""
        query = "La cuantía es $500,000,000"
        filters = self.extractor.extract_filters(query)
        
        assert 'cuantia_normalized' in filters
        assert filters['cuantia_normalized'] == '500000000'
    
    def test_extract_tipo_medida_from_real_case(self):
        """Test de extracción de tipo de medida con caso real"""
        query = "El tipo de medida es embargo"
        filters = self.extractor.extract_filters(query)
        
        assert 'tipo_medida' in filters
        assert filters['tipo_medida'] == 'Embargo'
    
    def test_validate_filters_with_real_data(self):
        """Test de validación de filtros con datos reales"""
        filters = {
            'demandante_normalized': '  COORDINADORA COMERCIAL DE CARGAS CCC SA  ',
            'cuantia_normalized': '500000000',
            'empty_filter': ''
        }
        
        validated = self.extractor.validate_filters(filters)
        
        assert 'demandante_normalized' in validated
        assert 'coordinadora comercial de cargas ccc sa' in validated['demandante_normalized']
        assert 'cuantia_normalized' in validated
        assert 'empty_filter' not in validated
    
    def test_no_filters_for_general_queries(self):
        """Test de que no se extraen filtros para consultas generales"""
        query = "¿Qué información tienes sobre expedientes?"
        filters = self.extractor.extract_filters(query)
        
        # No debería extraer filtros para consultas generales
        assert not filters or 'demandante_normalized' not in filters 