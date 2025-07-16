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
                    json_path = os.path.join(JSON_DOCS_PATH, json_file, "output.json")
                    
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