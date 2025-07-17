"""
Tests unitarios para el sistema de indexación universal
"""
import pytest
import tempfile
import os
import json
from src.indexing.chroma_indexer import ChromaIndexer
from src.chunking.document_chunker import Chunk

class TestChromaIndexerUniversal:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        # Usar directorio temporal para tests
        self.temp_dir = tempfile.mkdtemp()
        self.indexer = ChromaIndexer(persist_directory=self.temp_dir)
    
    def teardown_method(self):
        """Limpiar después de cada test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_normalize_metadata_universal(self):
        """Test de normalización universal de metadatos"""
        metadata = {
            'demandante': 'NÚRY WILLÉLMA ROMERO GÓMEZ',
            'demandado': 'MUNICIPIO DE ARAUCA',
            'fecha': '2025-07-14',
            'cuantia': '$238.984.000,00',
            'nested_field': {
                'sub_field': 'valor anidado',
                'numbers': [1, 2, 3]
            }
        }
        
        normalized = self.indexer._normalize_metadata_universal(metadata)
        
        # Verificar campos básicos normalizados
        assert 'demandante' in normalized
        assert 'demandado' in normalized
        assert 'fecha' in normalized
        assert 'cuantia' in normalized
        
        # Verificar metadatos de indexación
        assert 'indexed_at' in normalized
        assert 'indexing_version' in normalized
        assert normalized['indexing_version'] == 'universal_v2'
        
        # Verificar normalización de strings
        assert normalized['demandante'] == 'nury willelma romero gomez'
        assert normalized['demandado'] == 'municipio de arauca'
    
    def test_normalize_field_name(self):
        """Test de normalización de nombres de campos"""
        # Test con espacios y caracteres especiales
        assert self.indexer._normalize_field_name('Nombre Empresa') == 'nombre_empresa'
        assert self.indexer._normalize_field_name('TipoIdentificación') == 'tipo_identificacion'
        assert self.indexer._normalize_field_name('Número_Identificación') == 'numero_identificacion'
        assert self.indexer._normalize_field_name('Cuantía$') == 'cuantia'
    
    def test_normalize_value_by_type(self):
        """Test de normalización de valores por tipo"""
        # Test con string
        assert self.indexer._normalize_value_by_type('JUAN PÉREZ') == 'juan perez'
        
        # Test con números
        assert self.indexer._normalize_value_by_type(500000) == 500000
        assert self.indexer._normalize_value_by_type(3.14) == 3.14
        
        # Test con boolean
        assert self.indexer._normalize_value_by_type(True) == True
        
        # Test con listas y diccionarios
        assert self.indexer._normalize_value_by_type([1, 2, 3]) == '[1, 2, 3]'
        assert self.indexer._normalize_value_by_type({'key': 'value'}) == "{'key': 'value'}"
    
    def test_normalize_string_value(self):
        """Test de normalización específica de strings"""
        # Test con texto con tildes
        assert self.indexer._normalize_string_value('NÚRY WILLÉLMA') == 'nury willelma'
        
        # Test con espacios extra
        assert self.indexer._normalize_string_value('  JUAN   PÉREZ  ') == 'juan perez'
        
        # Test con string vacío
        assert self.indexer._normalize_string_value('') == ''
        assert self.indexer._normalize_string_value(None) == ''
    
    def test_repair_and_parse_json_valid(self):
        """Test de reparación y parseo de JSON válido"""
        valid_json = '{"demandante": {"nombres": "JUAN", "apellidos": "PÉREZ"}}'
        result = self.indexer._repair_and_parse_json(valid_json)
        
        assert result is not None
        assert 'demandante' in result
        assert result['demandante']['nombres'] == 'JUAN'
    
    def test_repair_and_parse_json_malformed(self):
        """Test de reparación y parseo de JSON mal formateado"""
        malformed_json = '{"demandante": {"nombres": "JUAN", "apellidos": "PÉREZ",}}'  # Coma extra
        result = self.indexer._repair_and_parse_json(malformed_json)
        
        assert result is not None
        assert 'demandante' in result
        assert result['demandante']['nombres'] == 'JUAN'
    
    def test_repair_and_parse_json_invalid(self):
        """Test de reparación y parseo de JSON inválido"""
        invalid_json = '{"demandante": {"nombres": "JUAN", "apellidos": "PÉREZ"'  # Sin cerrar
        result = self.indexer._repair_and_parse_json(invalid_json)
        
        # Debería intentar reparar y fallar
        assert result is None
    
    def test_basic_json_repair(self):
        """Test de reparación básica de JSON"""
        # Test con comas finales
        malformed = '{"key": "value",}'
        repaired = self.indexer._basic_json_repair(malformed)
        assert repaired == '{"key": "value"}'
        
        # Test con caracteres de control
        malformed = '{"key": "value\u0000"}'
        repaired = self.indexer._basic_json_repair(malformed)
        assert '\u0000' not in repaired
        
        # Test con espacios extra
        malformed = '  {"key": "value"}  '
        repaired = self.indexer._basic_json_repair(malformed)
        assert repaired == '{"key": "value"}'
    
    def test_extract_all_metadata_recursive(self):
        """Test de extracción recursiva de metadatos"""
        test_data = {
            'demandante': {
                'persona': {
                    'nombres': 'MARÍA',
                    'apellidos': 'GARCÍA',
                    'identificacion': {
                        'tipo': 'CC',
                        'numero': '12345678'
                    }
                },
                'empresa': {
                    'nombre': 'EMPRESA ABC',
                    'nit': '900123456-7'
                }
            },
            'resoluciones': [
                {'numero': '001', 'fecha': '2024-01-01'},
                {'numero': '002', 'fecha': '2024-01-02'}
            ]
        }
        
        metadata = self.indexer._extract_all_metadata_recursive(test_data)
        
        # Verificar campos anidados
        assert 'demandante_persona_nombres' in metadata
        assert 'demandante_persona_apellidos' in metadata
        assert 'demandante_persona_identificacion_tipo' in metadata
        assert 'demandante_persona_identificacion_numero' in metadata
        assert 'demandante_empresa_nombre' in metadata
        assert 'demandante_empresa_nit' in metadata
        
        # Verificar arrays
        assert 'resoluciones_0_numero' in metadata
        assert 'resoluciones_0_fecha' in metadata
        assert 'resoluciones_1_numero' in metadata
        assert 'resoluciones_1_fecha' in metadata
        
        # Verificar valores
        assert metadata['demandante_persona_nombres'] == 'MARÍA'
        assert metadata['demandante_persona_identificacion_tipo'] == 'CC'
        assert metadata['resoluciones_0_numero'] == '001'
    
    def test_generate_embeddings(self):
        """Test de generación de embeddings"""
        texts = ["texto de prueba 1", "texto de prueba 2"]
        embeddings = self.indexer._generate_embeddings(texts)
        
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 768  # Dimensiones del modelo paraphrase-multilingual-mpnet-base-v2
    
    def test_prepare_chunks_for_indexing_universal(self):
        """Test de preparación de chunks para indexación universal"""
        # Crear chunks de prueba
        chunks = [
            Chunk(
                id="test_1",
                text="Texto de prueba 1",
                position=1,
                total_chunks=2,
                metadata={
                    'document_id': 'test',
                    'demandante': 'JUAN PÉREZ',
                    'nested_field': {
                        'sub_field': 'valor anidado'
                    }
                },
                start_token=0,
                end_token=10
            ),
            Chunk(
                id="test_2",
                text="Texto de prueba 2",
                position=2,
                total_chunks=2,
                metadata={
                    'document_id': 'test',
                    'demandante': 'JUAN PÉREZ',
                    'fecha': '2024-01-15'
                },
                start_token=10,
                end_token=20
            )
        ]

        texts, metadatas, ids = self.indexer._prepare_chunks_for_indexing(chunks)

        assert len(texts) == 2
        assert len(metadatas) == 2
        assert len(ids) == 2

        assert texts[0] == "Texto de prueba 1"
        assert texts[1] == "Texto de prueba 2"
        assert ids[0] == "test_1"
        assert ids[1] == "test_2"

        # Verificar metadatos normalizados universalmente
        assert 'demandante' in metadatas[0]
        assert metadatas[0]['demandante'] == 'juan perez'
        assert 'indexed_at' in metadatas[0]
        assert 'indexing_version' in metadatas[0]
        assert metadatas[0]['indexing_version'] == 'universal_v2'

        # Verificar que los campos anidados se serializan como string
        assert 'nested_field' in metadatas[0]
        assert isinstance(metadatas[0]['nested_field'], str)
        assert 'sub_field' in metadatas[0]['nested_field']
    
    def test_index_document_universal(self):
        """Test de indexación universal de documento"""
        document_id = "test_doc_universal"
        text = "Este es un documento de prueba para indexación universal. " * 10
        metadata = {
            'document_id': document_id,
            'demandante': 'JUAN PÉREZ',
            'fecha': '2024-01-15',
            'cuantia': 500000,
            'nested_data': {
                'sub_field': 'valor anidado',
                'numbers': [1, 2, 3]
            }
        }
        
        result = self.indexer.index_document(document_id, text, metadata)
        
        assert result['success'] == True
        assert result['document_id'] == document_id
        assert result['chunks_indexed'] > 0
        assert 'metadata_fields_indexed' in result
        assert result['metadata_fields_indexed'] > 0
        assert 'indexed_at' in result
    
    def test_index_batch_universal(self):
        """Test de indexación universal de lote"""
        documents = [
            {
                'id': 'doc1',
                'text': 'Texto del documento 1. ' * 10,
                'metadata': {
                    'demandante': 'JUAN PÉREZ',
                    'fecha': '2024-01-15'
                }
            },
            {
                'id': 'doc2',
                'text': 'Texto del documento 2. ' * 10,
                'metadata': {
                    'demandante': 'MARÍA GARCÍA',
                    'fecha': '2024-01-16',
                    'nested_field': {
                        'sub_field': 'valor anidado'
                    }
                }
            }
        ]
        
        result = self.indexer.index_batch(documents)
        
        assert result['total_documents'] == 2
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert result['success_rate'] == 100.0
        assert len(result['results']) == 2
    
    def test_get_collection_stats_universal(self):
        """Test de estadísticas de colección con versión universal"""
        stats = self.indexer.get_collection_stats()
        
        assert 'collection_name' in stats
        assert 'total_chunks' in stats
        assert 'indexing_version' in stats
        assert stats['indexing_version'] == 'universal_v2'
    
    def test_search_similar_universal(self):
        """Test de búsqueda similar con metadatos universales"""
        # Primero indexar un documento
        document_id = "test_search_universal"
        text = "Este es un documento sobre Juan Pérez que solicita una medida cautelar."
        metadata = {
            'document_id': document_id,
            'demandante': 'JUAN PÉREZ',
            'fecha': '2024-01-15',
            'tipo_medida': 'embargo'
        }
        
        self.indexer.index_document(document_id, text, metadata)
        
        # Realizar búsqueda
        result = self.indexer.search_similar("Juan Pérez", n_results=5)
        
        assert 'query' in result
        assert 'results' in result
        assert 'total_results' in result
        assert result['query'] == "Juan Pérez"
        assert result['total_results'] > 0
    
    def test_compatibility_with_legacy_metadata(self):
        """Test de compatibilidad con metadatos legacy"""
        # Usar el método legacy de normalización
        metadata = {
            'demandante': 'NÚRY WILLÉLMA ROMERO GÓMEZ',
            'demandado': 'MUNICIPIO DE ARAUCA',
            'fecha': '2025-07-14',
            'cuantia': '$238.984.000,00'
        }
        
        normalized = self.indexer._normalize_metadata(metadata)
        
        # Verificar que funciona como antes
        assert 'demandante_normalized' in normalized
        assert 'demandado_normalized' in normalized
        assert 'fecha_normalized' in normalized
        assert 'cuantia_normalized' in normalized
        assert 'indexed_at' in normalized
        
        # Verificar normalización específica
        assert normalized['demandante_normalized'] == 'nury willelma romero gomez'
        assert normalized['demandado_normalized'] == 'municipio de arauca' 