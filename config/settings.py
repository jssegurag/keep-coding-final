"""
Configuración centralizada del sistema RAG para expedientes jurídicos.

Este módulo contiene todas las configuraciones necesarias para el MVP RAG,
siguiendo principios de configuración centralizada y separación de responsabilidades.
"""

import os
from typing import Final
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la API de Google
GOOGLE_API_KEY: Final[str] = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL: Final[str] = "gemini-2.0-flash-lite"  # Modelo económico para MVP

# Configuración de embeddings
EMBEDDING_MODEL: Final[str] = "paraphrase-multilingual-mpnet-base-v2"  # Modelo optimizado para textos legales
EMBEDDING_DIMENSIONS: Final[int] = 768

# Configuración de chunking
CHUNK_SIZE: Final[int] = 512
CHUNK_OVERLAP: Final[int] = 50

# Configuración de ChromaDB
CHROMA_PERSIST_DIRECTORY: Final[str] = "data/chroma_db"
CHROMA_COLLECTION_NAME: Final[str] = "legal_documents"

# Configuración de SQLite para metadatos canónicos
SQLITE_DB_PATH: Final[str] = "data/legal_docs.db"

# Configuración de archivos
CSV_METADATA_PATH: Final[str] = "src/resources/metadata/studio_results_20250715_2237.csv"
TARGET_PATH: Final[str] = "target/"
JSON_DOCS_PATH: Final[str] = "target/"

# Configuración de testing
TEST_DOCS_COUNT: Final[int] = 5  # Documentos para validación de embeddings
TEST_QUESTIONS_COUNT: Final[int] = 10  # Preguntas para validación inicial
VALIDATION_QUESTIONS_COUNT: Final[int] = 20  # Preguntas para evaluación cualitativa

# Configuración de logging
LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE: Final[str] = "logs/rag_system.log"

# Configuración de validación
MAX_CHUNK_SIZE: Final[int] = 1024  # Tamaño máximo para fallback recursivo
MIN_CHUNK_SIZE: Final[int] = 50  # Tamaño mínimo de chunk 