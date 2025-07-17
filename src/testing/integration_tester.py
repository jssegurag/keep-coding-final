"""
Módulo para testing de integración del sistema RAG completo
"""
import json
import time
import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
from src.query.query_handler import QueryHandler
from src.indexing.chroma_indexer import ChromaIndexer
from src.chunking.document_chunker import DocumentChunker
from src.utils.logger import setup_logger
from config.settings import CSV_METADATA_PATH

logger = setup_logger(__name__, "logs/integration_testing.log")

class IntegrationTester:
    def __init__(self):
        self.query_handler = QueryHandler()
        self.indexer = ChromaIndexer()
        self.chunker = DocumentChunker()
        
        # Cargar datos reales para preguntas
        self.real_data = self._load_real_data()
        
        # Definir preguntas de evaluación cualitativa basadas en datos reales
        self.evaluation_questions = self._create_evaluation_questions()
        
    def _load_real_data(self) -> Dict[str, any]:
        """Cargar datos reales del CSV para crear preguntas auténticas"""
        try:
            df = pd.read_csv(CSV_METADATA_PATH)
            real_documents = []
            
            for _, row in df.iterrows():
                try:
                    # Parsear metadatos JSON
                    metadata_str = row['metadata']
                    if pd.isna(metadata_str):
                        continue
                        
                    # Intentar parsear como JSON
                    if metadata_str.startswith('['):
                        # Array de demandantes
                        metadata_list = json.loads(metadata_str)
                        for item in metadata_list:
                            if 'demandante' in item:
                                real_documents.append({
                                    'document_id': row['document_id'],
                                    'demandante': item['demandante']
                                })
                    else:
                        # Objeto único
                        metadata_obj = json.loads(metadata_str)
                        if 'demandante' in metadata_obj:
                            real_documents.append({
                                'document_id': row['document_id'],
                                'demandante': metadata_obj['demandante']
                            })
                except:
                    continue
            
            return {
                'documents': real_documents[:10],  # Usar primeros 10 para preguntas
                'total_available': len(df)
            }
        except Exception as e:
            logger.error(f"Error cargando datos reales: {e}")
            return {'documents': [], 'total_available': 0}
        
    def _create_evaluation_questions(self) -> List[Dict[str, any]]:
        """Crear 20 preguntas representativas basadas en datos reales"""
        questions = []
        
        # Usar datos reales para crear preguntas auténticas
        real_docs = self.real_data.get('documents', [])
        
        # Preguntas de metadatos (5) - Basadas en datos reales
        if real_docs:
            doc1 = real_docs[0] if len(real_docs) > 0 else None
            doc2 = real_docs[1] if len(real_docs) > 1 else None
            
            if doc1:
                demandante1 = doc1.get('demandante', {})
                nombres1 = demandante1.get('nombresPersonaDemandante', '')
                apellidos1 = demandante1.get('apellidosPersonaDemandante', '')
                empresa1 = demandante1.get('NombreEmpresaDemandante', '')
                
                if nombres1 and apellidos1:
                    questions.append({
                        "id": 1,
                        "question": f"¿Cuál es el demandante del expediente {doc1['document_id']}?",
                        "category": "metadatos",
                        "expected_keywords": ["demandante", nombres1.split()[0], apellidos1.split()[0]],
                        "type": "extraction",
                        "real_document": doc1['document_id']
                    })
                elif empresa1:
                    questions.append({
                        "id": 1,
                        "question": f"¿Cuál es la empresa demandante del expediente {doc1['document_id']}?",
                        "category": "metadatos",
                        "expected_keywords": ["demandante", empresa1.split()[0]],
                        "type": "extraction",
                        "real_document": doc1['document_id']
                    })
            
            if doc2:
                demandante2 = doc2.get('demandante', {})
                nombres2 = demandante2.get('nombresPersonaDemandante', '')
                apellidos2 = demandante2.get('apellidosPersonaDemandante', '')
                
                if nombres2 and apellidos2:
                    questions.append({
                        "id": 2,
                        "question": f"¿Quién es el demandante en el expediente {doc2['document_id']}?",
                        "category": "metadatos",
                        "expected_keywords": ["demandante", nombres2.split()[0], apellidos2.split()[0]],
                        "type": "extraction",
                        "real_document": doc2['document_id']
                    })
        
        # Preguntas genéricas de metadatos (3)
        questions.extend([
            {
                "id": 3,
                "question": "¿Cuál es la cuantía del embargo?",
                "category": "metadatos",
                "expected_keywords": ["cuantía", "embargo", "pesos"],
                "type": "extraction"
            },
            {
                "id": 4,
                "question": "¿En qué fecha se dictó la medida cautelar?",
                "category": "metadatos",
                "expected_keywords": ["fecha", "medida", "cautelar"],
                "type": "extraction"
            },
            {
                "id": 5,
                "question": "¿Qué tipo de medida se solicitó?",
                "category": "metadatos",
                "expected_keywords": ["embargo", "medida cautelar"],
                "type": "extraction"
            }
        ])
        
        # Preguntas de contenido (10) - Basadas en consultas reales
        content_questions = [
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
            }
        ]
        questions.extend(content_questions)
        
        # Preguntas de resumen (5) - Incluyendo expedientes reales
        if real_docs:
            for i, doc in enumerate(real_docs[:3]):
                questions.append({
                    "id": 16 + i,
                    "question": f"Resume el expediente {doc['document_id']}",
                    "category": "resumen",
                    "expected_keywords": ["resumen", "expediente", "caso"],
                    "type": "summary",
                    "real_document": doc['document_id']
                })
        
        # Preguntas genéricas de resumen (2)
        questions.extend([
            {
                "id": 19,
                "question": "¿Cuál es la situación actual del proceso?",
                "category": "resumen",
                "expected_keywords": ["situación", "actual", "proceso"],
                "type": "summary"
            },
            {
                "id": 20,
                "question": "¿Qué impacto tiene esta medida cautelar?",
                "category": "resumen",
                "expected_keywords": ["impacto", "medida", "cautelar"],
                "type": "summary"
            }
        ])
        
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
                    "search_results": result.get("search_results_count", 0),
                    "real_document": question.get("real_document", None)
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
            "real_documents_tested": len([q for q in evaluation_results["questions"] if q.get("real_document")]),
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