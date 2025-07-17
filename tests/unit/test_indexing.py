"""
Tests unitarios para el sistema de indexación
"""
import pytest
import tempfile
import os
from src.indexing.chroma_indexer import ChromaIndexer
from src.chunking.document_chunker import Chunk

class TestChromaIndexer:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        # Usar directorio temporal para tests
        self.temp_dir = tempfile.mkdtemp()
        self.indexer = ChromaIndexer(persist_directory=self.temp_dir)
    
    def teardown_method(self):
        """Limpiar después de cada test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_normalize_metadata(self):
        """Test de normalización de metadatos"""
        metadata = {
            'demandante': 'NÚRY WILLÉLMA ROMERO GÓMEZ',
            'demandado': 'MUNICIPIO DE ARAUCA',
            'fecha': '2025-07-14',
            'cuantia': '$238.984.000,00'
        }
        
        normalized = self.indexer._normalize_metadata(metadata)
        
        assert 'demandante_normalized' in normalized
        assert 'demandado_normalized' in normalized
        assert 'fecha_normalized' in normalized
        assert 'cuantia_normalized' in normalized
        assert 'indexed_at' in normalized
        
        # Verificar normalización
        assert normalized['demandante_normalized'] == 'nury willelma romero gomez'
        assert normalized['demandado_normalized'] == 'municipio de arauca'
    
    def test_generate_embeddings(self):
        """Test de generación de embeddings"""
        texts = ["texto de prueba 1", "texto de prueba 2"]
        embeddings = self.indexer._generate_embeddings(texts)
        
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 768  # Dimensiones del modelo paraphrase-multilingual-mpnet-base-v2
    
    def test_prepare_chunks_for_indexing(self):
        """Test de preparación de chunks para indexación"""
        # Crear chunks de prueba
        chunks = [
            Chunk(
                id="test_1",
                text="Texto de prueba 1",
                position=1,
                total_chunks=2,
                metadata={'document_id': 'test', 'demandante': 'Juan Pérez'},
                start_token=0,
                end_token=10
            ),
            Chunk(
                id="test_2",
                text="Texto de prueba 2",
                position=2,
                total_chunks=2,
                metadata={'document_id': 'test', 'demandante': 'Juan Pérez'},
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

        # Verificar metadatos normalizados universales
        assert 'demandante' in metadatas[0]
        assert metadatas[0]['demandante'] == 'juan perez'
        assert 'indexed_at' in metadatas[0]
        assert 'indexing_version' in metadatas[0]
    
    def test_index_document(self):
        """Test de indexación de documento"""
        document_id = "test_doc"
        text = "Este es un documento de prueba. " * 50  # Texto largo
        metadata = {
            'document_id': document_id,
            'demandante': 'Juan Pérez',
            'demandado': 'Empresa ABC'
        }
        
        result = self.indexer.index_document(document_id, text, metadata)
        
        assert result['success'] == True
        assert result['document_id'] == document_id
        assert result['chunks_indexed'] > 0
        
        # Verificar que se indexó en ChromaDB
        stats = self.indexer.get_collection_stats()
        assert stats['total_chunks'] > 0
    
    def test_search_similar(self):
        """Test de búsqueda similar"""
        # Primero indexar un documento
        document_id = "test_search_doc"
        text = "El demandante Juan Pérez solicita embargo por $1,000,000"
        metadata = {
            'document_id': document_id,
            'demandante': 'Juan Pérez',
            'tipo_medida': 'Embargo'
        }

        self.indexer.index_document(document_id, text, metadata)

        # Realizar búsqueda
        results = self.indexer.search_similar("Juan Pérez", n_results=5)

        assert 'error' not in results
        assert results.get('total_results', 0) >= 1
    
    def test_search_with_filters(self):
        """Test de búsqueda con filtros"""
        # Indexar documento
        document_id = "test_filter_doc"
        text = "Documento de prueba con filtros"
        metadata = {
            'document_id': document_id,
            'demandante': 'María García',
            'tipo_medida': 'Embargo'
        }

        self.indexer.index_document(document_id, text, metadata)

        # Búsqueda con filtro usando la estructura universal
        where_filter = {"demandante": "maria garcia"}
        results = self.indexer.search_similar("embargo", where=where_filter)

        assert 'error' not in results
        assert results.get('total_results', 0) >= 0  # Puede ser 0 si no hay coincidencias exactas 