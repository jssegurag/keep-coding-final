# 02. Validación de Embeddings para Textos Legales - MVP RAG

## 🎯 Objetivo
Validar que el modelo de embeddings `paraphrase-multilingual-mpnet-base-v2` funciona correctamente con textos legales colombianos antes de indexar todo el corpus.

## 📋 Tareas a Ejecutar

### 1. Crear Módulo de Validación de Embeddings
Crear `src/testing/embedding_validator.py`:
```python
"""
Módulo para validar embeddings con textos legales
Siguiendo principios SOLID y GRASP
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import json
import os
from config.settings import EMBEDDING_MODEL, CSV_METADATA_PATH, JSON_DOCS_PATH

class EmbeddingValidator:
    """
    Validador de embeddings para textos legales colombianos.
    Responsabilidad única: Validar la calidad de embeddings para el dominio legal.
    """
    
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.test_documents = []
        self.test_questions = []
        self.expected_answers = []
        
    def load_test_documents(self) -> List[Dict]:
        """
        Cargar 5 documentos representativos para testing.
        Adaptado a la estructura actual de datos.
        """
        try:
            # Cargar metadatos
            df = pd.read_csv(CSV_METADATA_PATH)
            
            # Obtener lista de archivos JSON disponibles
            available_files = self._get_available_json_files()
            print(f"Archivos JSON disponibles: {len(available_files)}")
            
            # Seleccionar documentos que tengan archivos JSON correspondientes
            test_docs = []
            for _, doc in df.head(10).iterrows():  # Revisar más documentos para encontrar coincidencias
                filename = self._extract_filename_from_path(doc['documentname'])
                
                # Buscar archivo JSON correspondiente
                json_file = self._find_matching_json_file(filename, available_files)
                
                if json_file:
                    json_path = os.path.join(JSON_DOCS_PATH, f"{json_file}/output.json")
                    
                    if os.path.exists(json_path):
                        with open(json_path, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            # Extraer texto de la estructura DoclingDocument
                            doc_dict = doc.to_dict()
                            doc_dict['content'] = self._extract_text_from_docling(content)
                            doc_dict['chunks'] = self._create_test_chunks(doc_dict['content'])
                            # Extraer metadatos del JSON anidado
                            doc_dict.update(self._extract_metadata_from_response(doc['response']))
                            test_docs.append(doc_dict)
                            
                            if len(test_docs) >= 5:  # Limitar a 5 documentos
                                break
            
            self.test_documents = test_docs
            print(f"Documentos cargados exitosamente: {len(test_docs)}")
            return test_docs
            
        except Exception as e:
            print(f"Error cargando documentos de prueba: {e}")
            return []
    
    def _get_available_json_files(self) -> List[str]:
        """Obtener lista de directorios con archivos output.json"""
        available_files = []
        if os.path.exists(JSON_DOCS_PATH):
            for item in os.listdir(JSON_DOCS_PATH):
                item_path = os.path.join(JSON_DOCS_PATH, item)
                if os.path.isdir(item_path):
                    json_path = os.path.join(item_path, "output.json")
                    if os.path.exists(json_path):
                        available_files.append(item)
        return available_files
    
    def _find_matching_json_file(self, csv_filename: str, available_files: List[str]) -> Optional[str]:
        """Encontrar archivo JSON que coincida con el nombre del CSV"""
        # Buscar coincidencia exacta
        for file in available_files:
            if csv_filename in file or file.replace('.pdf', '') == csv_filename:
                return file
        
        # Si no hay coincidencia exacta, buscar coincidencia parcial
        for file in available_files:
            if csv_filename[:8] in file:  # Usar primeros 8 caracteres
                return file
        
        return None
    
    def _extract_filename_from_path(self, path: str) -> str:
        """Extraer nombre del archivo del path completo"""
        return os.path.basename(path).replace('.pdf', '')
    
    def _extract_text_from_docling(self, docling_content: Dict) -> str:
        """Extraer texto de la estructura DoclingDocument"""
        try:
            texts = []
            if 'texts' in docling_content:
                for text_obj in docling_content['texts']:
                    if 'text' in text_obj:
                        texts.append(text_obj['text'])
            return ' '.join(texts)
        except Exception as e:
            print(f"Error extrayendo texto: {e}")
            return ""
    
    def _extract_metadata_from_response(self, response_str: str) -> Dict:
        """Extraer metadatos del JSON anidado en la respuesta"""
        try:
            # Parsear el JSON anidado
            response_data = json.loads(response_str)
            
            metadata = {}
            
            # Extraer demandante
            if isinstance(response_data, list) and len(response_data) > 0:
                first_item = response_data[0]
                if 'demandante' in first_item:
                    demandante = first_item['demandante']
                    if demandante.get('nombresPersonaDemandante') and demandante.get('apellidosPersonaDemandante'):
                        metadata['demandante'] = f"{demandante['nombresPersonaDemandante']} {demandante['apellidosPersonaDemandante']}"
                    elif demandante.get('NombreEmpresaDemandante'):
                        metadata['demandante'] = demandante['NombreEmpresaDemandante']
                    else:
                        metadata['demandante'] = "No especificado"
            elif isinstance(response_data, dict) and 'demandante' in response_data:
                demandante = response_data['demandante']
                if demandante.get('nombresPersonaDemandante') and demandante.get('apellidosPersonaDemandante'):
                    metadata['demandante'] = f"{demandante['nombresPersonaDemandante']} {demandante['apellidosPersonaDemandante']}"
                elif demandante.get('NombreEmpresaDemandante'):
                    metadata['demandante'] = demandante['NombreEmpresaDemandante']
                else:
                    metadata['demandante'] = "No especificado"
            
            return metadata
            
        except Exception as e:
            print(f"Error extrayendo metadatos: {e}")
            return {'demandante': 'No especificado'}
    
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
            if 'chunks' not in doc or not doc['chunks']:
                continue
                
            # Generar embeddings para chunks
            chunk_embeddings = self.generate_embeddings(doc['chunks'])
            
            # Crear consultas relacionadas
            queries = [
                f"demandante {doc.get('demandante', '')}",
                f"documento legal",
                f"expediente judicial",
                f"resolución"
            ]
            
            query_embeddings = self.generate_embeddings(queries)
            
            # Calcular similitud coseno
            similarities = []
            for query_emb in query_embeddings:
                for chunk_emb in chunk_embeddings:
                    similarity = np.dot(query_emb, chunk_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(chunk_emb))
                    similarities.append(similarity)
            
            results[doc.get('documentname', 'unknown')] = np.mean(similarities)
        
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
                doc['demandante'].split()[0] if ' ' in doc['demandante'] else doc['demandante']
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
            
            results[doc.get('documentname', 'unknown')] = np.max(similarities)
        
        return results
    
    def test_legal_concepts(self) -> Dict[str, float]:
        """Probar búsqueda por conceptos jurídicos"""
        legal_concepts = [
            "embargo", "demanda", "medida cautelar", "fundamento jurídico",
            "hechos", "pruebas", "sentencia", "recurso", "apelación",
            "resolución", "expediente", "juez", "tribunal"
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
            
            results[doc.get('documentname', 'unknown')] = np.mean(similarities)
        
        return results
    
    def run_validation(self) -> Dict[str, any]:
        """Ejecutar validación completa"""
        print("Iniciando validación de embeddings...")
        
        # Cargar documentos
        docs = self.load_test_documents()
        if not docs:
            return {"error": "No se pudieron cargar documentos de prueba"}
        
        print(f"Cargados {len(docs)} documentos de prueba")
        
        # Crear preguntas
        questions = self.create_test_questions()
        print(f"Creadas {len(questions)} preguntas de prueba")
        
        # Ejecutar tests
        semantic_results = self.test_semantic_similarity()
        name_results = self.test_name_search()
        concept_results = self.test_legal_concepts()
        
        # Calcular métricas
        avg_semantic = np.mean(list(semantic_results.values())) if semantic_results else 0
        avg_name = np.mean(list(name_results.values())) if name_results else 0
        avg_concept = np.mean(list(concept_results.values())) if concept_results else 0
        
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
            print(f"Error en validación: {results['error']}")
            return
        
        print("\nResultados de Validación de Embeddings")
        print("=" * 50)
        
        metrics = results["metrics"]
        print(f"Similitud Semántica Promedio: {metrics['avg_semantic_similarity']:.3f}")
        print(f"Búsqueda por Nombres Promedio: {metrics['avg_name_search']:.3f}")
        print(f"Conceptos Jurídicos Promedio: {metrics['avg_legal_concepts']:.3f}")
        print(f"Puntuación General: {metrics['overall_score']:.3f}")
        
        # Evaluar resultados
        if metrics['overall_score'] >= 0.7:
            print("Embeddings validados - Apto para producción")
        elif metrics['overall_score'] >= 0.5:
            print("Embeddings aceptables - Considerar optimizaciones")
        else:
            print("Embeddings no satisfactorios - Evaluar modelo alternativo")
```

### 2. Crear Script de Validación
Crear `scripts/validate_embeddings.py`:
```python
#!/usr/bin/env python3
"""
Script para validar embeddings con textos legales
Siguiendo principios SOLID y GRASP
"""
import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.testing.embedding_validator import EmbeddingValidator

def main():
    """
    Función principal del script de validación.
    Responsabilidad única: Orquestar el proceso de validación.
    """
    print("Iniciando validación de embeddings...")
    
    try:
        # Crear validador
        validator = EmbeddingValidator()
        
        # Ejecutar validación
        results = validator.run_validation()
        
        # Imprimir resultados
        validator.print_results(results)
        
        # Guardar resultados
        save_results(results)
        
        print("Validación completada. Resultados guardados en logs/embedding_validation_results.json")
        
    except Exception as e:
        print(f"Error durante la validación: {e}")
        sys.exit(1)

def save_results(results: dict):
    """
    Guardar resultados de validación en archivo JSON.
    Responsabilidad única: Persistencia de resultados.
    """
    try:
        # Crear directorio logs si no existe
        os.makedirs("logs", exist_ok=True)
        
        # Guardar resultados
        with open("logs/embedding_validation_results.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error guardando resultados: {e}")

if __name__ == "__main__":
    main()
```

### 3. Crear Tests Unitarios
Crear `tests/unit/test_embedding_validator.py`:
```python
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
```

### 4. Crear Configuración de Logging
Crear `src/utils/logger.py`:
```python
"""
Configuración de logging para el proyecto
Siguiendo principios SOLID y GRASP
"""
import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configurar logger para el módulo.
    Responsabilidad única: Configuración de logging.
    
    Args:
        name: Nombre del logger
        log_file: Ruta del archivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Formato sin emojis como especifica el documento
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
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_validation_logger() -> logging.Logger:
    """
    Obtener logger específico para validación de embeddings.
    Responsabilidad única: Logger especializado para validación.
    
    Returns:
        Logger configurado para validación
    """
    return setup_logger(
        'embedding_validator',
        'logs/embedding_validation.log'
    )

def get_testing_logger() -> logging.Logger:
    """
    Obtener logger específico para testing.
    Responsabilidad única: Logger especializado para testing.
    
    Returns:
        Logger configurado para testing
    """
    return setup_logger(
        'testing',
        'logs/testing.log'
    )
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
- Adaptado a la estructura de datos real del proyecto 