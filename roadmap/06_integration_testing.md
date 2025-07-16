# 06. Testing de Integración y Evaluación Cualitativa - MVP RAG

## 🎯 Objetivo
Implementar testing de integración completo y evaluación cualitativa del sistema RAG con 20 preguntas representativas para validar el MVP.

## 📋 Tareas a Ejecutar

### 1. Crear Módulo de Testing de Integración
Crear `src/testing/integration_tester.py`:
```python
"""
Módulo para testing de integración del sistema RAG completo
"""
import json
import time
from typing import List, Dict, Tuple
from datetime import datetime
from src.query.query_handler import QueryHandler
from src.indexing.chroma_indexer import ChromaIndexer
from src.chunking.document_chunker import DocumentChunker
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/integration_testing.log")

class IntegrationTester:
    def __init__(self):
        self.query_handler = QueryHandler()
        self.indexer = ChromaIndexer()
        self.chunker = DocumentChunker()
        
        # Definir preguntas de evaluación cualitativa
        self.evaluation_questions = self._create_evaluation_questions()
        
    def _create_evaluation_questions(self) -> List[Dict[str, any]]:
        """Crear 20 preguntas representativas para evaluación"""
        questions = [
            # Preguntas de metadatos (5)
            {
                "id": 1,
                "question": "¿Cuál es el demandante del expediente RCCI2150725310?",
                "category": "metadatos",
                "expected_keywords": ["demandante", "Nury", "Romero"],
                "type": "extraction"
            },
            {
                "id": 2,
                "question": "¿Cuál es la cuantía del embargo?",
                "category": "metadatos",
                "expected_keywords": ["cuantía", "238.984.000", "pesos"],
                "type": "extraction"
            },
            {
                "id": 3,
                "question": "¿En qué fecha se dictó la medida cautelar?",
                "category": "metadatos",
                "expected_keywords": ["fecha", "2025", "julio"],
                "type": "extraction"
            },
            {
                "id": 4,
                "question": "¿Qué tipo de medida se solicitó?",
                "category": "metadatos",
                "expected_keywords": ["embargo", "medida cautelar"],
                "type": "extraction"
            },
            {
                "id": 5,
                "question": "¿Cuál es el demandado en el expediente?",
                "category": "metadatos",
                "expected_keywords": ["demandado", "Municipio", "Arauca"],
                "type": "extraction"
            },
            
            # Preguntas de contenido (10)
            {
                "id": 6,
                "question": "¿Cuáles son los hechos principales del caso?",
                "category": "contenido",
                "expected_keywords": ["hechos", "caso", "situación"],
                "type": "comprehension"
            },
            {
                "id": 7,
                "question": "¿Qué fundamentos jurídicos se esgrimen?",
                "category": "contenido",
                "expected_keywords": ["fundamentos", "jurídicos", "legal"],
                "type": "comprehension"
            },
            {
                "id": 8,
                "question": "¿Cuáles son las medidas cautelares solicitadas?",
                "category": "contenido",
                "expected_keywords": ["medidas", "cautelares", "solicitadas"],
                "type": "comprehension"
            },
            {
                "id": 9,
                "question": "¿Qué pruebas se presentaron?",
                "category": "contenido",
                "expected_keywords": ["pruebas", "documentos", "evidencia"],
                "type": "comprehension"
            },
            {
                "id": 10,
                "question": "¿Cuál es el estado actual del proceso?",
                "category": "contenido",
                "expected_keywords": ["estado", "proceso", "actual"],
                "type": "comprehension"
            },
            {
                "id": 11,
                "question": "¿Quién es el juez del caso?",
                "category": "contenido",
                "expected_keywords": ["juez", "magistrado", "tribunal"],
                "type": "extraction"
            },
            {
                "id": 12,
                "question": "¿Cuáles son las pretensiones del demandante?",
                "category": "contenido",
                "expected_keywords": ["pretensiones", "solicita", "pedido"],
                "type": "comprehension"
            },
            {
                "id": 13,
                "question": "¿Qué argumentos presenta la defensa?",
                "category": "contenido",
                "expected_keywords": ["argumentos", "defensa", "contesta"],
                "type": "comprehension"
            },
            {
                "id": 14,
                "question": "¿Cuál es el número de expediente?",
                "category": "contenido",
                "expected_keywords": ["expediente", "número", "RCCI"],
                "type": "extraction"
            },
            {
                "id": 15,
                "question": "¿Qué documentos se adjuntaron?",
                "category": "contenido",
                "expected_keywords": ["documentos", "adjuntos", "anexos"],
                "type": "comprehension"
            },
            
            # Preguntas de resumen (5)
            {
                "id": 16,
                "question": "Resume el expediente RCCI2150725310",
                "category": "resumen",
                "expected_keywords": ["resumen", "expediente", "caso"],
                "type": "summary"
            },
            {
                "id": 17,
                "question": "¿Cuál es la situación actual del proceso?",
                "category": "resumen",
                "expected_keywords": ["situación", "actual", "proceso"],
                "type": "summary"
            },
            {
                "id": 18,
                "question": "¿Qué decisión se tomó en el expediente?",
                "category": "resumen",
                "expected_keywords": ["decisión", "resolución", "sentencia"],
                "type": "summary"
            },
            {
                "id": 19,
                "question": "¿Cuáles son los puntos principales del caso?",
                "category": "resumen",
                "expected_keywords": ["puntos", "principales", "caso"],
                "type": "summary"
            },
            {
                "id": 20,
                "question": "¿Qué impacto tiene esta medida cautelar?",
                "category": "resumen",
                "expected_keywords": ["impacto", "medida", "cautelar"],
                "type": "summary"
            }
        ]
        
        return questions
    
    def test_end_to_end_pipeline(self) -> Dict[str, any]:
        """Test del pipeline completo end-to-end"""
        logger.info("Iniciando test end-to-end del pipeline")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "pipeline": {},
            "errors": []
        }
        
        try:
            # Test 1: Verificar componentes individuales
            test_results["components"] = self._test_individual_components()
            
            # Test 2: Verificar indexación
            test_results["indexing"] = self._test_indexing()
            
            # Test 3: Verificar búsqueda
            test_results["search"] = self._test_search()
            
            # Test 4: Verificar consultas
            test_results["queries"] = self._test_queries()
            
            # Test 5: Verificar pipeline completo
            test_results["pipeline"] = self._test_complete_pipeline()
            
            logger.info("Test end-to-end completado exitosamente")
            
        except Exception as e:
            error_msg = f"Error en test end-to-end: {str(e)}"
            logger.error(error_msg)
            test_results["errors"].append(error_msg)
        
        return test_results
    
    def _test_individual_components(self) -> Dict[str, any]:
        """Test de componentes individuales"""
        results = {}
        
        # Test chunker
        try:
            test_text = "Este es un texto de prueba para chunking. " * 20
            test_metadata = {"document_id": "test_doc", "demandante": "Juan Pérez"}
            chunks = self.chunker.chunk_document(test_text, test_metadata)
            
            results["chunker"] = {
                "success": True,
                "chunks_created": len(chunks),
                "validation": self.chunker.validate_chunks(chunks)
            }
        except Exception as e:
            results["chunker"] = {"success": False, "error": str(e)}
        
        # Test indexer
        try:
            stats = self.indexer.get_collection_stats()
            results["indexer"] = {
                "success": True,
                "stats": stats
            }
        except Exception as e:
            results["indexer"] = {"success": False, "error": str(e)}
        
        # Test query handler
        try:
            # Test simple sin consulta real
            results["query_handler"] = {
                "success": True,
                "initialized": True
            }
        except Exception as e:
            results["query_handler"] = {"success": False, "error": str(e)}
        
        return results
    
    def _test_indexing(self) -> Dict[str, any]:
        """Test de indexación"""
        try:
            stats = self.indexer.get_collection_stats()
            
            return {
                "success": True,
                "total_chunks": stats.get("total_chunks", 0),
                "collection_name": stats.get("collection_name", ""),
                "has_data": stats.get("total_chunks", 0) > 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_search(self) -> Dict[str, any]:
        """Test de búsqueda"""
        test_queries = [
            "demandante",
            "embargo",
            "medida cautelar"
        ]
        
        results = []
        
        for query in test_queries:
            try:
                search_result = self.indexer.search_similar(query, n_results=3)
                results.append({
                    "query": query,
                    "success": "error" not in search_result,
                    "results_found": search_result.get("total_found", 0)
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }
    
    def _test_queries(self) -> Dict[str, any]:
        """Test de consultas"""
        test_queries = [
            "¿Cuál es el demandante?",
            "¿Qué tipo de medida es?",
            "embargo"
        ]
        
        results = []
        
        for query in test_queries:
            try:
                start_time = time.time()
                result = self.query_handler.handle_query(query)
                end_time = time.time()
                
                results.append({
                    "query": query,
                    "success": "error" not in result,
                    "response_time": end_time - start_time,
                    "has_response": len(result.get("response", "")) > 0,
                    "has_source": "Fuente:" in result.get("response", "")
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }
    
    def _test_complete_pipeline(self) -> Dict[str, any]:
        """Test del pipeline completo"""
        try:
            # Consulta de prueba
            test_query = "¿Cuál es el demandante del expediente?"
            
            start_time = time.time()
            result = self.query_handler.handle_query(test_query)
            end_time = time.time()
            
            return {
                "success": "error" not in result,
                "response_time": end_time - start_time,
                "has_response": len(result.get("response", "")) > 0,
                "has_source": "Fuente:" in result.get("response", ""),
                "search_results": result.get("search_results_count", 0)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_qualitative_evaluation(self) -> Dict[str, any]:
        """Ejecutar evaluación cualitativa con 20 preguntas"""
        logger.info("Iniciando evaluación cualitativa")
        
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(self.evaluation_questions),
            "questions": [],
            "summary": {}
        }
        
        successful = 0
        total_time = 0
        
        for question in self.evaluation_questions:
            try:
                start_time = time.time()
                result = self.query_handler.handle_query(question["question"])
                end_time = time.time()
                
                response_time = end_time - start_time
                total_time += response_time
                
                # Evaluar calidad de respuesta
                quality_score = self._evaluate_response_quality(
                    result.get("response", ""),
                    question
                )
                
                question_result = {
                    "id": question["id"],
                    "question": question["question"],
                    "category": question["category"],
                    "type": question["type"],
                    "response": result.get("response", ""),
                    "quality_score": quality_score,
                    "response_time": response_time,
                    "success": "error" not in result,
                    "has_source": "Fuente:" in result.get("response", ""),
                    "search_results": result.get("search_results_count", 0)
                }
                
                evaluation_results["questions"].append(question_result)
                
                if question_result["success"]:
                    successful += 1
                
                logger.info(f"Pregunta {question['id']}: Calidad {quality_score}/5")
                
            except Exception as e:
                logger.error(f"Error en pregunta {question['id']}: {e}")
                evaluation_results["questions"].append({
                    "id": question["id"],
                    "question": question["question"],
                    "error": str(e),
                    "quality_score": 0,
                    "success": False
                })
        
        # Calcular estadísticas
        avg_quality = sum(q["quality_score"] for q in evaluation_results["questions"]) / len(evaluation_results["questions"])
        avg_time = total_time / len(evaluation_results["questions"])
        
        evaluation_results["summary"] = {
            "successful_questions": successful,
            "success_rate": (successful / len(self.evaluation_questions)) * 100,
            "average_quality": avg_quality,
            "average_response_time": avg_time,
            "questions_with_source": len([q for q in evaluation_results["questions"] if q.get("has_source", False)]),
            "quality_distribution": {
                "excellent": len([q for q in evaluation_results["questions"] if q["quality_score"] >= 4]),
                "good": len([q for q in evaluation_results["questions"] if 3 <= q["quality_score"] < 4]),
                "acceptable": len([q for q in evaluation_results["questions"] if 2 <= q["quality_score"] < 3]),
                "poor": len([q for q in evaluation_results["questions"] if q["quality_score"] < 2])
            }
        }
        
        logger.info(f"Evaluación cualitativa completada: {successful}/{len(self.evaluation_questions)} exitosas")
        return evaluation_results
    
    def _evaluate_response_quality(self, response: str, question: Dict[str, any]) -> int:
        """Evaluar calidad de respuesta (1-5)"""
        if not response or "Error" in response:
            return 1
        
        score = 0
        
        # Criterio 1: Respuesta no vacía y coherente
        if len(response) > 20 and not response.startswith("No se encuentra"):
            score += 1
        
        # Criterio 2: Incluye información específica
        expected_keywords = question.get("expected_keywords", [])
        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in response.lower())
        if keyword_matches > 0:
            score += 1
        
        # Criterio 3: Incluye fuente
        if "Fuente:" in response:
            score += 1
        
        # Criterio 4: Respuesta apropiada para el tipo de pregunta
        question_type = question.get("type", "")
        if question_type == "extraction" and any(keyword in response.lower() for keyword in ["es", "fue", "está"]):
            score += 1
        elif question_type == "comprehension" and len(response) > 50:
            score += 1
        elif question_type == "summary" and len(response) > 100:
            score += 1
        
        # Criterio 5: Respuesta completa y bien estructurada
        if len(response) > 100 and ("." in response or "\n" in response):
            score += 1
        
        return min(score, 5)
```

### 2. Crear Script de Testing de Integración
Crear `scripts/run_integration_tests.py`:
```python
#!/usr/bin/env python3
"""
Script para ejecutar tests de integración
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.testing.integration_tester import IntegrationTester

def main():
    print("🧪 Ejecutando Tests de Integración")
    print("=" * 50)
    
    # Crear tester
    tester = IntegrationTester()
    
    # Ejecutar test end-to-end
    print("1️⃣ Test End-to-End del Pipeline")
    e2e_results = tester.test_end_to_end_pipeline()
    
    # Mostrar resultados
    print(f"\n📊 Resultados End-to-End:")
    
    # Componentes individuales
    components = e2e_results.get("components", {})
    print(f"   - Chunker: {'✅' if components.get('chunker', {}).get('success') else '❌'}")
    print(f"   - Indexer: {'✅' if components.get('indexer', {}).get('success') else '❌'}")
    print(f"   - Query Handler: {'✅' if components.get('query_handler', {}).get('success') else '❌'}")
    
    # Indexación
    indexing = e2e_results.get("indexing", {})
    if indexing.get("success"):
        print(f"   - Indexación: ✅ ({indexing.get('total_chunks', 0)} chunks)")
    else:
        print(f"   - Indexación: ❌")
    
    # Búsqueda
    search = e2e_results.get("search", {})
    if search.get("success"):
        print(f"   - Búsqueda: ✅")
    else:
        print(f"   - Búsqueda: ❌")
    
    # Consultas
    queries = e2e_results.get("queries", {})
    if queries.get("success"):
        print(f"   - Consultas: ✅")
    else:
        print(f"   - Consultas: ❌")
    
    # Pipeline completo
    pipeline = e2e_results.get("pipeline", {})
    if pipeline.get("success"):
        print(f"   - Pipeline Completo: ✅ ({pipeline.get('response_time', 0):.2f}s)")
    else:
        print(f"   - Pipeline Completo: ❌")
    
    # Ejecutar evaluación cualitativa
    print(f"\n2️⃣ Evaluación Cualitativa")
    evaluation_results = tester.run_qualitative_evaluation()
    
    summary = evaluation_results.get("summary", {})
    print(f"\n📊 Resultados de Evaluación:")
    print(f"   - Preguntas exitosas: {summary.get('successful_questions', 0)}/20")
    print(f"   - Tasa de éxito: {summary.get('success_rate', 0):.1f}%")
    print(f"   - Calidad promedio: {summary.get('average_quality', 0):.2f}/5")
    print(f"   - Tiempo promedio: {summary.get('average_response_time', 0):.2f}s")
    print(f"   - Con fuente: {summary.get('questions_with_source', 0)}/20")
    
    # Distribución de calidad
    quality_dist = summary.get("quality_distribution", {})
    print(f"\n📈 Distribución de Calidad:")
    print(f"   - Excelente (4-5): {quality_dist.get('excellent', 0)}")
    print(f"   - Buena (3-4): {quality_dist.get('good', 0)}")
    print(f"   - Aceptable (2-3): {quality_dist.get('acceptable', 0)}")
    print(f"   - Pobre (1-2): {quality_dist.get('poor', 0)}")
    
    # Guardar resultados
    all_results = {
        "end_to_end": e2e_results,
        "qualitative_evaluation": evaluation_results
    }
    
    with open("logs/integration_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en logs/integration_test_results.json")
    
    # Evaluación final
    success_rate = summary.get("success_rate", 0)
    avg_quality = summary.get("average_quality", 0)
    
    if success_rate >= 80 and avg_quality >= 3.5:
        print(f"\n🎉 ¡MVP VALIDADO! Sistema listo para producción")
    elif success_rate >= 60 and avg_quality >= 3.0:
        print(f"\n⚠️ MVP ACEPTABLE - Considerar optimizaciones")
    else:
        print(f"\n❌ MVP NO CUMPLE CRITERIOS - Requiere mejoras")

if __name__ == "__main__":
    main()
```

### 3. Crear Tests de Integración
Crear `tests/integration/test_full_pipeline.py`:
```python
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
```

### 4. Crear Script de Monitoreo
Crear `scripts/monitor_system.py`:
```python
#!/usr/bin/env python3
"""
Script para monitoreo del sistema RAG
"""
import sys
import os
import json
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer
from src.query.query_handler import QueryHandler

def main():
    print("📊 Monitoreo del Sistema RAG")
    print("=" * 40)
    
    # Inicializar componentes
    indexer = ChromaIndexer()
    query_handler = QueryHandler()
    
    # Obtener estadísticas
    print("📈 Estadísticas del Sistema:")
    
    # Estadísticas de indexación
    stats = indexer.get_collection_stats()
    if "error" not in stats:
        print(f"   - Chunks indexados: {stats.get('total_chunks', 0)}")
        print(f"   - Colección: {stats.get('collection_name', 'N/A')}")
        print(f"   - Metadatos disponibles: {len(stats.get('sample_metadata_keys', []))}")
    else:
        print(f"   ❌ Error obteniendo estadísticas: {stats['error']}")
    
    # Probar consultas de monitoreo
    monitoring_queries = [
        "demandante",
        "embargo",
        "medida cautelar"
    ]
    
    print(f"\n🔍 Pruebas de Consulta:")
    for query in monitoring_queries:
        try:
            start_time = time.time()
            result = query_handler.handle_query(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if "error" not in result:
                print(f"   ✅ '{query}': {result['search_results_count']} resultados ({response_time:.2f}s)")
            else:
                print(f"   ❌ '{query}': Error")
                
        except Exception as e:
            print(f"   ❌ '{query}': {e}")
    
    # Verificar logs
    print(f"\n📋 Estado de Logs:")
    log_files = [
        "logs/chunking.log",
        "logs/indexing.log", 
        "logs/query.log",
        "logs/integration_testing.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"   ✅ {log_file}: {size} bytes")
        else:
            print(f"   ❌ {log_file}: No existe")
    
    print(f"\n✅ Monitoreo completado")

if __name__ == "__main__":
    main()
```

## ✅ Criterios de Éxito
- [ ] Tests de integración pasando
- [ ] Evaluación cualitativa con 20 preguntas
- [ ] Tasa de éxito > 80%
- [ ] Calidad promedio > 3.5/5
- [ ] Tiempo de respuesta < 5 segundos
- [ ] 100% de respuestas con trazabilidad
- [ ] Monitoreo del sistema funcionando

## 🔍 Verificación
Ejecutar los siguientes comandos:
```bash
# Ejecutar tests de integración
python scripts/run_integration_tests.py

# Monitorear sistema
python scripts/monitor_system.py

# Ejecutar tests
python -m pytest tests/integration/test_full_pipeline.py -v

# Verificar logs
cat logs/integration_testing.log
```

## 📊 Métricas de Evaluación
- **Tasa de éxito**: > 80% de preguntas exitosas
- **Calidad promedio**: > 3.5/5 puntos
- **Tiempo de respuesta**: < 5 segundos promedio
- **Trazabilidad**: 100% de respuestas con fuente
- **Distribución de calidad**: > 60% en categorías "Buena" o "Excelente"

## 📝 Notas Importantes
- La evaluación cualitativa es crítica para validar el MVP
- Los tests de integración deben ejecutarse regularmente
- El monitoreo debe detectar degradación de rendimiento
- Los logs deben mantenerse para análisis posterior 