"""
Tests unitarios para la configuración del sistema RAG.

Validación de que la configuración se carga correctamente
y contiene todos los parámetros necesarios.
"""

import pytest
from typing import Any
from config.settings import (
    GOOGLE_API_KEY, GOOGLE_MODEL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS,
    CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_PERSIST_DIRECTORY, CHROMA_COLLECTION_NAME,
    SQLITE_DB_PATH, TEST_DOCS_COUNT, TEST_QUESTIONS_COUNT, VALIDATION_QUESTIONS_COUNT
)


class TestConfiguration:
    """Tests para validar la configuración del sistema."""
    
    def test_google_api_configuration(self) -> None:
        """Validar configuración de API de Google."""
        assert isinstance(GOOGLE_API_KEY, str)
        assert isinstance(GOOGLE_MODEL, str)
        assert GOOGLE_MODEL == "gemini-2.0-flash-lite"
    
    def test_embedding_configuration(self) -> None:
        """Validar configuración de embeddings."""
        assert isinstance(EMBEDDING_MODEL, str)
        assert EMBEDDING_MODEL == "paraphrase-multilingual-mpnet-base-v2"
        assert isinstance(EMBEDDING_DIMENSIONS, int)
        assert EMBEDDING_DIMENSIONS == 512
    
    def test_chunking_configuration(self) -> None:
        """Validar configuración de chunking."""
        assert isinstance(CHUNK_SIZE, int)
        assert CHUNK_SIZE == 512
        assert isinstance(CHUNK_OVERLAP, int)
        assert CHUNK_OVERLAP == 50
        assert CHUNK_OVERLAP < CHUNK_SIZE
    
    def test_chromadb_configuration(self) -> None:
        """Validar configuración de ChromaDB."""
        assert isinstance(CHROMA_PERSIST_DIRECTORY, str)
        assert CHROMA_PERSIST_DIRECTORY == "data/chroma_db"
        assert isinstance(CHROMA_COLLECTION_NAME, str)
        assert CHROMA_COLLECTION_NAME == "legal_documents"
    
    def test_sqlite_configuration(self) -> None:
        """Validar configuración de SQLite."""
        assert isinstance(SQLITE_DB_PATH, str)
        assert SQLITE_DB_PATH == "data/legal_docs.db"
    
    def test_testing_configuration(self) -> None:
        """Validar configuración de testing."""
        assert isinstance(TEST_DOCS_COUNT, int)
        assert TEST_DOCS_COUNT == 5
        assert isinstance(TEST_QUESTIONS_COUNT, int)
        assert TEST_QUESTIONS_COUNT == 10
        assert isinstance(VALIDATION_QUESTIONS_COUNT, int)
        assert VALIDATION_QUESTIONS_COUNT == 20
    
    def test_configuration_types(self) -> None:
        """Validar tipos de datos de configuración."""
        config_vars = [
            GOOGLE_API_KEY, GOOGLE_MODEL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS,
            CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_PERSIST_DIRECTORY, 
            CHROMA_COLLECTION_NAME, SQLITE_DB_PATH, TEST_DOCS_COUNT,
            TEST_QUESTIONS_COUNT, VALIDATION_QUESTIONS_COUNT
        ]
        
        for var in config_vars:
            assert var is not None, f"Variable de configuración no puede ser None"
    
    def test_chunking_parameters_validity(self) -> None:
        """Validar que los parámetros de chunking son coherentes."""
        assert CHUNK_SIZE > 0, "CHUNK_SIZE debe ser positivo"
        assert CHUNK_OVERLAP >= 0, "CHUNK_OVERLAP debe ser no negativo"
        assert CHUNK_OVERLAP < CHUNK_SIZE, "CHUNK_OVERLAP debe ser menor que CHUNK_SIZE"
    
    def test_testing_parameters_validity(self) -> None:
        """Validar que los parámetros de testing son coherentes."""
        assert TEST_DOCS_COUNT > 0, "TEST_DOCS_COUNT debe ser positivo"
        assert TEST_QUESTIONS_COUNT > 0, "TEST_QUESTIONS_COUNT debe ser positivo"
        assert VALIDATION_QUESTIONS_COUNT > 0, "VALIDATION_QUESTIONS_COUNT debe ser positivo"
        assert VALIDATION_QUESTIONS_COUNT >= TEST_QUESTIONS_COUNT, "VALIDATION_QUESTIONS_COUNT debe ser >= TEST_QUESTIONS_COUNT" 