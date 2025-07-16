# 04. Implementación del Sistema de Indexación - MVP RAG

## 🎯 Objetivo
Implementar el sistema de indexación en ChromaDB con normalización de metadatos, generación de embeddings y almacenamiento de chunks para búsqueda híbrida.

## 📋 Tareas a Ejecutar

### 1. Crear Módulo de Indexación
Crear `src/indexing/chroma_indexer.py`:
```python
"""
Módulo para indexación en ChromaDB con normalización de metadatos
"""
import chromadb
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import json
import os
from datetime import datetime
from config.settings import (
    CHROMA_PERSIST_DIRECTORY, 
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    CSV_METADATA_PATH,
    JSON_DOCS_PATH
)
from src.chunking.document_chunker import DocumentChunker, Chunk
from src.utils.text_utils import normalize_text, clean_text_for_chunking
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/indexing.log")

class ChromaIndexer:
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIRECTORY):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.chunker = DocumentChunker()
        self.logger = logger
        
        # Crear o obtener colección
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        """Obtener colección existente o crear nueva"""
        try:
            # Intentar obtener colección existente
            collection = self.client.get_collection(CHROMA_COLLECTION_NAME)
            self.logger.info(f"Colección existente cargada: {CHROMA_COLLECTION_NAME}")
            return collection
        except:
            # Crear nueva colección
            collection = self.client.create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"description": "Documentos legales indexados"}
            )
            self.logger.info(f"Nueva colección creada: {CHROMA_COLLECTION_NAME}")
            return collection
    
    def _normalize_metadata(self, metadata: Dict) -> Dict:
        """Normalizar metadatos para búsqueda consistente"""
        normalized = metadata.copy()
        
        # Normalizar nombres
        for key in ['demandante', 'demandado', 'entidad']:
            if key in normalized and normalized[key]:
                normalized[f"{key}_normalized"] = normalize_text(str(normalized[key]))
        
        # Normalizar fechas
        if 'fecha' in normalized and normalized['fecha']:
            try:
                # Intentar parsear fecha
                date_obj = pd.to_datetime(normalized['fecha'])
                normalized['fecha_normalized'] = date_obj.strftime('%Y-%m-%d')
            except:
                normalized['fecha_normalized'] = str(normalized['fecha'])
        
        # Normalizar cuantías
        if 'cuantia' in normalized and normalized['cuantia']:
            try:
                # Extraer solo números
                amount_str = str(normalized['cuantia'])
                amount_clean = ''.join(filter(str.isdigit, amount_str))
                normalized['cuantia_normalized'] = amount_clean
            except:
                normalized['cuantia_normalized'] = str(normalized['cuantia'])
        
        # Añadir timestamp de indexación
        normalized['indexed_at'] = datetime.now().isoformat()
        
        return normalized
    
    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generar embeddings para una lista de textos"""
        try:
            embeddings = self.embedding_model.encode(texts)
            self.logger.info(f"Embeddings generados para {len(texts)} textos")
            return embeddings
        except Exception as e:
            self.logger.error(f"Error generando embeddings: {e}")
            raise
    
    def _prepare_chunks_for_indexing(self, chunks: List[Chunk]) -> Tuple[List[str], List[Dict], List[str]]:
        """Preparar chunks para indexación en ChromaDB"""
        texts = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            # Texto del chunk
            texts.append(chunk.text)
            
            # Metadatos normalizados
            normalized_metadata = self._normalize_metadata(chunk.metadata)
            metadatas.append(normalized_metadata)
            
            # ID único
            ids.append(chunk.id)
        
        return texts, metadatas, ids
    
    def index_document(self, document_id: str, text: str, metadata: Dict) -> Dict[str, any]:
        """
        Indexar un documento completo
        
        Args:
            document_id: ID único del documento
            text: Texto completo del documento
            metadata: Metadatos del documento
            
        Returns:
            Resultado de la indexación
        """
        self.logger.info(f"Iniciando indexación de documento: {document_id}")
        
        try:
            # Limpiar texto
            cleaned_text = clean_text_for_chunking(text)
            
            # Crear chunks
            chunks = self.chunker.chunk_document(cleaned_text, metadata)
            
            if not chunks:
                self.logger.warning(f"No se pudieron crear chunks para documento: {document_id}")
                return {"success": False, "error": "No chunks created"}
            
            # Validar chunks
            validation = self.chunker.validate_chunks(chunks)
            
            # Preparar datos para indexación
            texts, metadatas, ids = self._prepare_chunks_for_indexing(chunks)
            
            # Generar embeddings
            embeddings = self._generate_embeddings(texts)
            
            # Indexar en ChromaDB
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            result = {
                "success": True,
                "document_id": document_id,
                "chunks_indexed": len(chunks),
                "validation": validation,
                "indexed_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Documento indexado exitosamente: {document_id} ({len(chunks)} chunks)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error indexando documento {document_id}: {e}")
            return {"success": False, "error": str(e), "document_id": document_id}
    
    def index_batch(self, documents: List[Dict]) -> Dict[str, any]:
        """
        Indexar un lote de documentos
        
        Args:
            documents: Lista de documentos con {'id', 'text', 'metadata'}
            
        Returns:
            Resultado del batch
        """
        self.logger.info(f"Iniciando indexación de lote: {len(documents)} documentos")
        
        results = []
        successful = 0
        failed = 0
        
        for doc in documents:
            result = self.index_document(
                document_id=doc['id'],
                text=doc['text'],
                metadata=doc['metadata']
            )
            
            results.append(result)
            
            if result['success']:
                successful += 1
            else:
                failed += 1
        
        batch_result = {
            "total_documents": len(documents),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(documents)) * 100,
            "results": results
        }
        
        self.logger.info(f"Batch completado: {successful} exitosos, {failed} fallidos")
        return batch_result
    
    def load_and_index_from_csv(self) -> Dict[str, any]:
        """
        Cargar documentos desde CSV e indexarlos
        """
        self.logger.info("Iniciando carga desde CSV")
        
        try:
            # Cargar metadatos
            df = pd.read_csv(CSV_METADATA_PATH)
            self.logger.info(f"CSV cargado: {len(df)} documentos")
            
            documents_to_index = []
            
            for _, row in df.iterrows():
                document_id = row['filename']
                metadata = row.to_dict()
                
                # Cargar contenido JSON
                json_path = os.path.join(JSON_DOCS_PATH, f"{document_id}.json")
                
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        text = content.get('text', '')
                    
                    documents_to_index.append({
                        'id': document_id,
                        'text': text,
                        'metadata': metadata
                    })
                else:
                    self.logger.warning(f"Archivo JSON no encontrado: {json_path}")
            
            # Indexar documentos
            result = self.index_batch(documents_to_index)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error cargando desde CSV: {e}")
            return {"success": False, "error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, any]:
        """Obtener estadísticas de la colección"""
        try:
            count = self.collection.count()
            
            # Obtener muestra de metadatos para análisis
            sample = self.collection.get(limit=10)
            
            stats = {
                "total_chunks": count,
                "collection_name": CHROMA_COLLECTION_NAME,
                "sample_metadata_keys": list(sample['metadatas'][0].keys()) if sample['metadatas'] else [],
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def search_similar(self, query: str, n_results: int = 10, where: Dict = None) -> Dict[str, any]:
        """
        Buscar chunks similares
        
        Args:
            query: Consulta de búsqueda
            n_results: Número de resultados
            where: Filtros de metadatos
            
        Returns:
            Resultados de búsqueda
        """
        try:
            # Generar embedding de la consulta
            query_embedding = self.embedding_model.encode([query])
            
            # Realizar búsqueda
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where
            )
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results['ids'][0]) if results['ids'] else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            return {"error": str(e), "query": query}
```

### 2. Crear Script de Indexación
Crear `scripts/index_documents.py`:
```python
#!/usr/bin/env python3
"""
Script para indexar documentos en ChromaDB
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer
from config.settings import CSV_METADATA_PATH, JSON_DOCS_PATH
import pandas as pd

def main():
    print("Iniciando indexación de documentos...")
    
    # Crear indexador
    indexer = ChromaIndexer()
    
    # Verificar archivos de entrada
    if not os.path.exists(CSV_METADATA_PATH):
        print(f"No se encontró el archivo CSV: {CSV_METADATA_PATH}")
        return
    
    if not os.path.exists(JSON_DOCS_PATH):
        print(f"No se encontró el directorio JSON: {JSON_DOCS_PATH}")
        return
    
    # Indexar documentos
    result = indexer.load_and_index_from_csv()
    
    if result.get('success', False):
        print(f"Indexación completada:")
        print(f"   - Documentos totales: {result['total_documents']}")
        print(f"   - Exitosos: {result['successful']}")
        print(f"   - Fallidos: {result['failed']}")
        print(f"   - Tasa de éxito: {result['success_rate']:.1f}%")
        
        # Mostrar estadísticas
        stats = indexer.get_collection_stats()
        print(f"\nEstadísticas de la colección:")
        print(f"   - Chunks totales: {stats['total_chunks']}")
        print(f"   - Nombre: {stats['collection_name']}")
        print(f"   - Metadatos disponibles: {', '.join(stats['sample_metadata_keys'])}")
        
    else:
        print(f"Error en indexación: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
```

### 3. Crear Tests Unitarios
Crear `tests/unit/test_indexing.py`:
```python
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
        assert embeddings.shape[1] == 512  # Dimensiones del modelo
    
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
        
        # Verificar metadatos normalizados
        assert 'demandante_normalized' in metadatas[0]
        assert metadatas[0]['demandante_normalized'] == 'juan perez'
    
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
        assert results['total_found'] > 0
        assert 'Juan Pérez' in str(results['results'])
    
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
        
        # Búsqueda con filtro
        where_filter = {"demandante_normalized": "maria garcia"}
        results = self.indexer.search_similar("embargo", where=where_filter)
        
        assert 'error' not in results
        assert results['total_found'] > 0
```

### 4. Crear Script de Verificación
Crear `scripts/verify_indexing.py`:
```python
#!/usr/bin/env python3
"""
Script para verificar la indexación
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer

def main():
    print("Verificando indexación...")
    
    # Crear indexador
    indexer = ChromaIndexer()
    
    # Obtener estadísticas
    stats = indexer.get_collection_stats()
    
    if 'error' in stats:
        print(f"Error obteniendo estadísticas: {stats['error']}")
        return
    
    print(f"Estadísticas de la colección:")
    print(f"   - Chunks totales: {stats['total_chunks']}")
    print(f"   - Colección: {stats['collection_name']}")
    print(f"   - Metadatos disponibles: {', '.join(stats['sample_metadata_keys'])}")
    
    # Probar búsquedas
    test_queries = [
        "demandante",
        "embargo",
        "medida cautelar",
        "Juan Pérez"
    ]
    
    print(f"\nProbando búsquedas:")
    for query in test_queries:
        results = indexer.search_similar(query, n_results=3)
        
        if 'error' in results:
            print(f"   '{query}': {results['error']}")
        else:
            print(f"   '{query}': {results['total_found']} resultados")
    
    print("\nVerificación completada")

if __name__ == "__main__":
    main()
```

## ✅ Criterios de Éxito
- [ ] Módulo `ChromaIndexer` implementado correctamente
- [ ] Normalización de metadatos funcionando
- [ ] Generación de embeddings integrada
- [ ] Indexación de documentos completada
- [ ] Búsqueda con filtros funcionando
- [ ] Tests unitarios pasando
- [ ] Estadísticas de colección disponibles

## 🔍 Verificación
Ejecutar los siguientes comandos:
```bash
# Indexar documentos
python scripts/index_documents.py

# Verificar indexación
python scripts/verify_indexing.py

# Ejecutar tests
python -m pytest tests/unit/test_indexing.py -v

# Verificar logs
cat logs/indexing.log
```

## 📊 Métricas de Calidad
- **Tasa de éxito de indexación**: > 90%
- **Chunks indexados**: Todos los documentos procesados
- **Metadatos normalizados**: Todos los campos requeridos
- **Búsquedas funcionando**: Consultas básicas y con filtros

## 📝 Notas Importantes
- La normalización de metadatos es crítica para búsquedas consistentes
- Los embeddings deben generarse eficientemente para grandes volúmenes
- La validación debe ejecutarse después de cada indexación
- Las estadísticas deben mantenerse para monitoreo

## 🔄 Ajustes Realizados

### Coherencia con Pasos Anteriores
1. **Importaciones corregidas**: Uso de `normalize_text` y `clean_text_for_chunking` desde `src.utils.text_utils`
2. **Estructura de Chunk**: Compatible con la clase `Chunk` del paso 3
3. **Validación integrada**: Uso del método `validate_chunks` del `DocumentChunker`
4. **Logging sin emojis**: Consistente con los estándares establecidos

### Mejoras Implementadas
1. **Normalización robusta**: Manejo de errores en parsing de fechas y cantidades
2. **Validación de chunks**: Integración con el sistema de validación del paso 3
3. **Manejo de errores**: Logging detallado y recuperación de errores
4. **Tests completos**: Cobertura de todos los métodos principales

### Integración con Sistema Existente
1. **Configuración centralizada**: Uso de `config.settings`
2. **Logger consistente**: Mismo patrón de logging que otros módulos
3. **Estructura de datos**: Compatible con el sistema de chunking implementado
4. **Rutas de archivos**: Alineadas con la estructura del proyecto 