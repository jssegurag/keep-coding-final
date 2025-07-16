# 02. Validación de Embeddings para Textos Legales - MVP RAG

## 🎯 Objetivo
Validar que el modelo de embeddings `paraphrase-multilingual-mpnet-base-v2` funciona correctamente con textos legales colombianos antes de indexar todo el corpus.

## 📋 Tareas a Ejecutar

### 1. Crear Módulo de Validación de Embeddings
Crear `src/testing/embedding_validator.py`:
```python
"""
Módulo para validar embeddings con textos legales
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import json
import os
from config.settings import EMBEDDING_MODEL, CSV_METADATA_PATH, JSON_DOCS_PATH

class EmbeddingValidator:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.test_documents = []
        self.test_questions = []
        self.expected_answers = []
        
    def load_test_documents(self) -> List[Dict]:
        """Cargar 5 documentos representativos para testing"""
        try:
            # Cargar metadatos
            df = pd.read_csv(CSV_METADATA_PATH)
            
            # Seleccionar 5 documentos diversos
            test_docs = df.head(5).to_dict('records')
            
            # Cargar contenido de JSON
            for doc in test_docs:
                json_path = os.path.join(JSON_DOCS_PATH, f"{doc['filename']}.json")
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                        doc['content'] = content.get('text', '')
                        doc['chunks'] = self._create_test_chunks(content.get('text', ''))
            
            self.test_documents = test_docs
            return test_docs
            
        except Exception as e:
            print(f"❌ Error cargando documentos de prueba: {e}")
            return []
    
    def _create_test_chunks(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Crear chunks de prueba del texto"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
        return chunks
    
    def create_test_questions(self) -> List[Tuple[str, str]]:
        """Crear 10 preguntas de prueba con respuestas esperadas"""
        questions = [
            ("¿Cuál es el demandante?", "demandante"),
            ("¿Cuál es el demandado?", "demandado"),
            ("¿Cuál es la cuantía?", "cuantia"),
            ("¿Qué tipo de medida es?", "tipo_medida"),
            ("¿En qué fecha se dictó?", "fecha"),
            ("¿Cuáles son los hechos principales?", "hechos"),
            ("¿Qué fundamentos jurídicos se esgrimen?", "fundamentos"),
            ("¿Cuáles son las medidas cautelares?", "medidas"),
            ("¿Quién es el juez?", "juez"),
            ("¿Cuál es el número de expediente?", "numero_expediente")
        ]
        
        self.test_questions = questions
        return questions
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generar embeddings para una lista de textos"""
        return self.model.encode(texts)
    
    def test_semantic_similarity(self) -> Dict[str, float]:
        """Probar similitud semántica entre textos relacionados"""
        results = {}
        
        for doc in self.test_documents:
            if 'chunks' not in doc:
                continue
                
            # Generar embeddings para chunks
            chunk_embeddings = self.generate_embeddings(doc['chunks'])
            
            # Crear consultas relacionadas
            queries = [
                f"demandante {doc.get('demandante', '')}",
                f"demandado {doc.get('demandado', '')}",
                f"cuantía {doc.get('cuantia', '')}",
                f"medida {doc.get('tipo_medida', '')}"
            ]
            
            query_embeddings = self.generate_embeddings(queries)
            
            # Calcular similitud coseno
            similarities = []
            for query_emb in query_embeddings:
                for chunk_emb in chunk_embeddings:
                    similarity = np.dot(query_emb, chunk_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb))
                    similarities.append(similarity)
            
            results[doc.get('filename', 'unknown')] = np.mean(similarities)
        
        return results
    
    def test_name_search(self) -> Dict[str, float]:
        """Probar búsqueda por nombres específicos"""
        results = {}
        
        for doc in self.test_documents:
            if 'chunks' not in doc or 'demandante' not in doc:
                continue
            
            # Crear consultas de nombres
            name_queries = [
                doc['demandante'],
                doc['demandante'].lower(),
                doc['demandante'].replace(' ', ''),
                doc['demandante'].split()[0]  # Solo primer nombre
            ]
            
            # Generar embeddings
            name_embeddings = self.generate_embeddings(name_queries)
            chunk_embeddings = self.generate_embeddings(doc['chunks'])
            
            # Calcular similitud
            similarities = []
            for name_emb in name_embeddings:
                for chunk_emb in chunk_embeddings:
                    similarity = np.dot(name_emb, chunk_emb) / (np.linalg.norm(name_emb) * np.linalg.norm(chunk_emb))
                    similarities.append(similarity)
            
            results[doc.get('filename', 'unknown')] = np.max(similarities)
        
        return results
    
    def test_legal_concepts(self) -> Dict[str, float]:
        """Probar búsqueda por conceptos jurídicos"""
        legal_concepts = [
            "embargo", "demanda", "medida cautelar", "fundamento jurídico",
            "hechos", "pruebas", "sentencia", "recurso", "apelación"
        ]
        
        results = {}
        
        for doc in self.test_documents:
            if 'chunks' not in doc:
                continue
            
            # Generar embeddings
            concept_embeddings = self.generate_embeddings(legal_concepts)
            chunk_embeddings = self.generate_embeddings(doc['chunks'])
            
            # Calcular similitud
            similarities = []
            for concept_emb in concept_embeddings:
                for chunk_emb in chunk_embeddings:
                    similarity = np.dot(concept_emb, chunk_emb) / (np.linalg.norm(concept_emb) * np.linalg.norm(chunk_emb))
                    similarities.append(similarity)
            
            results[doc.get('filename', 'unknown')] = np.mean(similarities)
        
        return results
    
    def run_validation(self) -> Dict[str, any]:
        """Ejecutar validación completa"""
        print("🔍 Iniciando validación de embeddings...")
        
        # Cargar documentos
        docs = self.load_test_documents()
        if not docs:
            return {"error": "No se pudieron cargar documentos de prueba"}
        
        print(f"✅ Cargados {len(docs)} documentos de prueba")
        
        # Crear preguntas
        questions = self.create_test_questions()
        print(f"✅ Creadas {len(questions)} preguntas de prueba")
        
        # Ejecutar tests
        semantic_results = self.test_semantic_similarity()
        name_results = self.test_name_search()
        concept_results = self.test_legal_concepts()
        
        # Calcular métricas
        avg_semantic = np.mean(list(semantic_results.values()))
        avg_name = np.mean(list(name_results.values()))
        avg_concept = np.mean(list(concept_results.values()))
        
        results = {
            "semantic_similarity": semantic_results,
            "name_search": name_results,
            "legal_concepts": concept_results,
            "metrics": {
                "avg_semantic_similarity": avg_semantic,
                "avg_name_search": avg_name,
                "avg_legal_concepts": avg_concept,
                "overall_score": (avg_semantic + avg_name + avg_concept) / 3
            }
        }
        
        return results
    
    def print_results(self, results: Dict[str, any]):
        """Imprimir resultados de validación"""
        if "error" in results:
            print(f"❌ Error en validación: {results['error']}")
            return
        
        print("\n📊 Resultados de Validación de Embeddings")
        print("=" * 50)
        
        metrics = results["metrics"]
        print(f"Similitud Semántica Promedio: {metrics['avg_semantic_similarity']:.3f}")
        print(f"Búsqueda por Nombres Promedio: {metrics['avg_name_search']:.3f}")
        print(f"Conceptos Jurídicos Promedio: {metrics['avg_legal_concepts']:.3f}")
        print(f"Puntuación General: {metrics['overall_score']:.3f}")
        
        # Evaluar resultados
        if metrics['overall_score'] >= 0.7:
            print("✅ Embeddings validados - Apto para producción")
        elif metrics['overall_score'] >= 0.5:
            print("⚠️ Embeddings aceptables - Considerar optimizaciones")
        else:
            print("❌ Embeddings no satisfactorios - Evaluar modelo alternativo")
```

### 2. Crear Script de Validación
Crear `scripts/validate_embeddings.py`:
```python
#!/usr/bin/env python3
"""
Script para validar embeddings con textos legales
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.testing.embedding_validator import EmbeddingValidator
import json

def main():
    print("🚀 Iniciando validación de embeddings...")
    
    # Crear validador
    validator = EmbeddingValidator()
    
    # Ejecutar validación
    results = validator.run_validation()
    
    # Imprimir resultados
    validator.print_results(results)
    
    # Guardar resultados
    with open("logs/embedding_validation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("✅ Validación completada. Resultados guardados en logs/embedding_validation_results.json")

if __name__ == "__main__":
    main()
```

### 3. Crear Tests Unitarios
Crear `tests/unit/test_embedding_validator.py`:
```python
"""
Tests unitarios para el validador de embeddings
"""
import pytest
import numpy as np
from src.testing.embedding_validator import EmbeddingValidator

class TestEmbeddingValidator:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.validator = EmbeddingValidator()
    
    def test_create_test_chunks(self):
        """Test de creación de chunks"""
        text = "Este es un texto de prueba " * 100  # Texto largo
        chunks = self.validator._create_test_chunks(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 100 for chunk in chunks)
        
        # Verificar overlap
        for i in range(len(chunks) - 1):
            overlap_text = chunks[i][-20:]  # Últimos 20 caracteres
            next_chunk_start = chunks[i + 1][:20]  # Primeros 20 caracteres
            assert overlap_text in chunks[i + 1]
    
    def test_generate_embeddings(self):
        """Test de generación de embeddings"""
        texts = ["texto de prueba 1", "texto de prueba 2"]
        embeddings = self.validator.generate_embeddings(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] == 512  # Dimensiones del modelo
    
    def test_semantic_similarity(self):
        """Test de similitud semántica"""
        # Crear documentos de prueba
        self.validator.test_documents = [
            {
                'filename': 'test1.json',
                'chunks': ['demandante Juan Pérez', 'demandado Empresa ABC'],
                'demandante': 'Juan Pérez',
                'demandado': 'Empresa ABC'
            }
        ]
        
        results = self.validator.test_semantic_similarity()
        
        assert 'test1.json' in results
        assert isinstance(results['test1.json'], float)
        assert 0 <= results['test1.json'] <= 1
    
    def test_name_search(self):
        """Test de búsqueda por nombres"""
        self.validator.test_documents = [
            {
                'filename': 'test1.json',
                'chunks': ['demandante Juan Pérez', 'demandado Empresa ABC'],
                'demandante': 'Juan Pérez'
            }
        ]
        
        results = self.validator.test_name_search()
        
        assert 'test1.json' in results
        assert isinstance(results['test1.json'], float)
        assert 0 <= results['test1.json'] <= 1
```

### 4. Crear Configuración de Logging
Crear `src/utils/logger.py`:
```python
"""
Configuración de logging para el proyecto
"""
import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """Configurar logger para el módulo"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
```

## ✅ Criterios de Éxito
- [ ] Módulo `EmbeddingValidator` implementado correctamente
- [ ] Script de validación ejecutándose sin errores
- [ ] Tests unitarios pasando
- [ ] Resultados de validación guardados en logs
- [ ] Métricas calculadas correctamente
- [ ] Evaluación automática de aptitud del modelo

## 🔍 Verificación
Ejecutar los siguientes comandos:
```bash
# Ejecutar validación
python scripts/validate_embeddings.py

# Ejecutar tests
python -m pytest tests/unit/test_embedding_validator.py -v

# Verificar resultados
cat logs/embedding_validation_results.json
```

## 📊 Métricas de Evaluación
- **Similitud Semántica**: > 0.7 (excelente), > 0.5 (aceptable)
- **Búsqueda por Nombres**: > 0.6 (excelente), > 0.4 (aceptable)
- **Conceptos Jurídicos**: > 0.6 (excelente), > 0.4 (aceptable)
- **Puntuación General**: > 0.7 (apto para producción)

## 📝 Notas Importantes
- La validación debe ejecutarse antes de indexar todo el corpus
- Si los resultados no son satisfactorios, evaluar modelos alternativos
- Los logs deben mantenerse para análisis posterior
- La validación debe ser reproducible y consistente 