"""
Módulo para manejo de consultas con Gemini y trazabilidad
"""
import google.generativeai as genai
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from config.settings import GOOGLE_API_KEY, GOOGLE_MODEL, QUERY_LOG_FILE
from src.indexing.chroma_indexer import ChromaIndexer
from src.utils.text_utils import normalize_text, extract_legal_entities
from src.utils.logger import setup_logger

logger = setup_logger(__name__, QUERY_LOG_FILE)

class QueryHandler:
    def __init__(self):
        # Configurar Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(GOOGLE_MODEL)
        
        # Inicializar indexador
        self.indexer = ChromaIndexer()
        
        # Configurar prompt estructurado
        self.prompt_template = self._create_prompt_template()
        
    def _create_prompt_template(self) -> str:
        """Crear template de prompt estructurado"""
        return """
Contexto: {context}

Pregunta del usuario: {query}

Instrucciones específicas:
- Si la pregunta busca un resumen, genera un resumen estructurado del expediente
- Si la pregunta es específica sobre contenido, responde basándote únicamente en el contexto proporcionado
- Si la pregunta es sobre metadatos (fechas, nombres, cuantías), extrae la información relevante
- Si la información no está en el contexto, responde: "No se encuentra en el expediente proporcionado."
- Responde en español de manera profesional y jurídica

Tareas posibles:
- Resumir el contenido legal
- Responder preguntas específicas del contenido
- Extraer campos clave como fechas, cuantías o nombres
- Identificar tipos de medidas cautelares

Respuesta:
"""
    
    def _extract_entities_from_query(self, query: str) -> Dict[str, any]:
        """Extraer entidades de la consulta usando el extractor de entidades legales"""
        return extract_legal_entities(query)
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, any]:
        """Extraer filtros de la consulta con validaciones menos restrictivas"""
        filters = {}
        
        # Normalizar consulta
        normalized_query = normalize_text(query)
        
        # Extraer entidades legales
        entities = extract_legal_entities(query)
        
        # PRIORIDAD 1: Extraer document_id si está disponible
        if entities['document_numbers']:
            filters['document_id'] = entities['document_numbers'][0]
            logger.info(f"Document ID extraído: {filters['document_id']}")
        
        # PRIORIDAD 2: Extraer fechas y cuantías (más confiables)
        if entities['dates']:
            filters['fecha_normalized'] = entities['dates'][0]
        
        if entities['amounts']:
            amount_clean = ''.join(filter(str.isdigit, entities['amounts'][0]))
            if len(amount_clean) >= 3:  # Al menos 3 dígitos para ser válido
                filters['cuantia_normalized'] = amount_clean
        
        # PRIORIDAD 3: Extraer tipos de medida específicos
        legal_terms = entities['legal_terms']
        if 'embargo' in legal_terms:
            filters['tipo_medida'] = 'Embargo'
        elif 'medida cautelar' in legal_terms:
            filters['tipo_medida'] = 'Medida Cautelar'
        
        # PRIORIDAD 4: Extraer nombres SOLO si son muy específicos y no son palabras comunes
        if entities['names']:
            # Filtrar nombres válidos (excluir palabras comunes)
            valid_names = []
            for name in entities['names']:
                name_clean = name.strip()
                if len(name_clean) > 3:
                    name_lower = name_clean.lower()
                    words = name_lower.split()
                    
                    # Lista expandida de palabras genéricas que no deben extraerse
                    generic_words = {
                        'informacion', 'información', 'hay', 'sobre', 'acerca', 'respecto',
                        'datos', 'detalles', 'particular', 'especifico', 'específico',
                        'cual', 'cuál', 'que', 'qué', 'como', 'cómo', 'donde', 'dónde',
                        'cuando', 'cuándo', 'porque', 'por qué', 'para', 'con', 'sin',
                        'sobre', 'bajo', 'entre', 'desde', 'hasta', 'durante', 'antes',
                        'después', 'mientras', 'aunque', 'pero', 'sin embargo', 'además',
                        'que', 'es', 'un', 'una', 'del', 'de', 'la', 'el', 'expediente', 
                        'demandante', 'cuál', 'cual', 'tienes', 'hay', 'coordinadora', 
                        'comercial', 'cargas', 'ccc', 'sa', 'resumen', 'dame', 'un',
                        'del', 'expediente', 'documento', 'caso', 'proceso', 'legal',
                        'juridico', 'jurídico', 'informacion', 'información', 'datos',
                        'detalles', 'particular', 'especifico', 'específico'
                    }
                    
                    # Verificar que no contenga palabras genéricas
                    if not any(word in generic_words for word in words):
                        # Verificar que no sea solo palabras genéricas
                        if not all(word in generic_words for word in words):
                            # Verificar que tenga al menos 2 palabras o sea un nombre válido
                            if len(words) >= 2 or len(name_clean) >= 5:
                                valid_names.append(name_clean)
            
            if valid_names:
                # Solo usar el primer nombre válido encontrado
                filters['demandante_normalized'] = normalize_text(valid_names[0])
        
        # Patrones específicos para consultas estructuradas (más estrictos)
        patterns = {
            'demandante': r'(?:el\s+)?demandante\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})',
            'demandado': r'(?:el\s+)?demandado\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})',
            'cuantia': r'(?:cuantía|monto|valor)\s+(?:es\s+)?(\$?[\d,\.]+)',
            'fecha': r'(?:fecha|día)\s+(?:es\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        }
        
        for filter_key, pattern in patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                if self._is_valid_filter_value(value, filter_key):
                    if filter_key == 'demandante':
                        filters['demandante_normalized'] = normalize_text(value)
                    elif filter_key == 'demandado':
                        filters['demandado_normalized'] = normalize_text(value)
                    elif filter_key == 'cuantia':
                        amount_clean = ''.join(filter(str.isdigit, value))
                        if len(amount_clean) >= 3:
                            filters['cuantia_normalized'] = amount_clean
                    elif filter_key == 'fecha':
                        filters['fecha_normalized'] = value
        
        return filters
    
    def _is_valid_filter_value(self, value: str, filter_type: str) -> bool:
        """Validar si un valor extraído es válido para el tipo de filtro"""
        if not value or len(value.strip()) < 2:
            return False
        
        value_lower = value.lower().strip()
        
        # Palabras genéricas que no deben extraerse
        generic_words = {
            'informacion', 'información', 'hay', 'sobre', 'acerca', 'respecto',
            'datos', 'detalles', 'particular', 'especifico', 'específico',
            'cual', 'cuál', 'que', 'qué', 'como', 'cómo', 'donde', 'dónde',
            'cuando', 'cuándo', 'porque', 'por qué', 'para', 'con', 'sin',
            'sobre', 'bajo', 'entre', 'desde', 'hasta', 'durante', 'antes',
            'después', 'mientras', 'aunque', 'pero', 'sin embargo', 'además'
        }
        
        # Validaciones específicas por tipo
        if filter_type in ['demandante', 'demandado']:
            # Verificar que no contenga palabras genéricas
            words = value_lower.split()
            if any(word in generic_words for word in words):
                return False
            
            # Verificar que tenga al menos 2 palabras o sea un nombre válido
            if len(words) < 2 and len(value.strip()) < 5:
                return False
            
            # Verificar que no sea solo palabras genéricas
            if all(word in generic_words for word in words):
                return False
        
        elif filter_type == 'cuantia':
            # Verificar que contenga números
            if not any(c.isdigit() for c in value):
                return False
        
        elif filter_type == 'fecha':
            # Verificar formato básico de fecha
            if not re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', value):
                return False
        
        return True
    
    def _convert_filters_to_chromadb_format(self, filters: Dict[str, any]) -> Dict[str, any]:
        """Convertir filtros al formato requerido por ChromaDB"""
        if not filters:
            return None
        
        chromadb_filters = {}
        
        for key, value in filters.items():
            if value:
                # ChromaDB requiere que los valores sean strings
                chromadb_filters[key] = str(value)
        
        return chromadb_filters
    
    def _format_context_for_prompt(self, search_results: Dict[str, any]) -> str:
        """Formatear contexto para el prompt"""
        try:
            if 'error' in search_results:
                return "No se encontraron documentos relevantes para la consulta."
            
            results = search_results.get('results', {})
            documents = results.get('documents', [[]])
            metadatas = results.get('metadatas', [[]])
            
            if not documents[0] or not metadatas[0]:
                return "No se encontraron documentos relevantes para la consulta."
            
            context_parts = []
            
            # Procesar documentos y metadatos
            docs = documents[0]
            metas = metadatas[0]
            
            for i, (doc, metadata) in enumerate(zip(docs, metas)):
                # Extraer información de fuente usando metadatos reales
                document_id = metadata.get('document_id', 'unknown')
                chunk_position = metadata.get('chunk_position', 0)
                total_chunks = metadata.get('total_chunks', 0)
                
                # Formatear chunk
                chunk_text = doc[:500] + "..." if len(doc) > 500 else doc
                chunk_info = f"[Chunk {chunk_position}/{total_chunks} del documento {document_id}]"
                
                context_parts.append(f"{chunk_info}\n{chunk_text}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error formateando contexto: {e}")
            return "No se encontraron documentos relevantes para la consulta."
    
    def _extract_source_info(self, search_results: Dict[str, any]) -> Dict[str, any]:
        """Extraer información de fuente de los resultados"""
        try:
            if 'error' in search_results:
                return {"document_id": "unknown", "chunk_position": 0, "total_chunks": 0}
            
            results = search_results.get('results', {})
            metadatas = results.get('metadatas', [])
            
            if not metadatas or not metadatas[0]:
                return {"document_id": "unknown", "chunk_position": 0, "total_chunks": 0}
            
            # Usar el primer resultado como fuente principal
            first_metadata = metadatas[0][0]
            
            return {
                "document_id": first_metadata.get('document_id', 'unknown'),
                "chunk_position": first_metadata.get('chunk_position', 0),
                "total_chunks": first_metadata.get('total_chunks', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo información de fuente: {e}")
            return {"document_id": "unknown", "chunk_position": 0, "total_chunks": 0}
    
    def handle_query(self, query: str, n_results: int = 10) -> Dict[str, any]:
        """
        Manejar consulta completa con estrategia híbrida robusta
        Args:
            query: Consulta del usuario
            n_results: Número de resultados a buscar
        Returns:
            Respuesta estructurada
        """
        logger.info(f"Procesando consulta: {query}")
        try:
            # Extraer entidades de la consulta
            entities = extract_legal_entities(query)
            filters = self._extract_filters_from_query(query)
            logger.info(f"Entidades extraídas: {entities}")
            logger.info(f"Filtros extraídos: {filters}")

            # ESTRATEGIA HÍBRIDA MEJORADA - MENOS RESTRICTIVA
            search_results = None
            search_strategy = "semantic"

            # PRIORIDAD 1: Búsqueda por document_id si está disponible
            if filters.get('document_id'):
                document_id = filters['document_id']
                logger.info(f"Buscando por document_id específico: {document_id}")
                
                # Búsqueda directa por document_id
                search_results = self.indexer.search_similar(
                    query=query,
                    n_results=n_results,
                    where={'document_id': document_id}
                )
                search_strategy = "document_id_exact"
                
                if search_results.get('total_results', 0) == 0:
                    logger.info(f"No se encontró el documento {document_id}, usando búsqueda semántica")
                    # Si no encuentra por document_id, usar búsqueda semántica
                    search_results = self.indexer.search_similar(
                        query=query,
                        n_results=n_results
                    )
                    search_strategy = "semantic_fallback"

            # PRIORIDAD 2: Búsqueda semántica con filtros opcionales (solo si son muy específicos)
            else:
                # Solo usar filtros muy específicos, no nombres genéricos
                chromadb_filters = self._convert_filters_to_chromadb_format(filters)
                use_filters = False
                
                if chromadb_filters:
                    # Solo usar filtros específicos como fechas, cuantías, tipos de medida
                    specific_filters = ['fecha_normalized', 'cuantia_normalized', 'tipo_medida']
                    if any(key in chromadb_filters for key in specific_filters):
                        # Remover filtros de nombres que pueden ser muy restrictivos
                        if 'demandante_normalized' in chromadb_filters:
                            del chromadb_filters['demandante_normalized']
                        if 'demandado_normalized' in chromadb_filters:
                            del chromadb_filters['demandado_normalized']
                        
                        if chromadb_filters:
                            use_filters = True
                            logger.info(f"Usando filtros específicos: {chromadb_filters}")
                
                search_results = self.indexer.search_similar(
                    query=query,
                    n_results=n_results,
                    where=chromadb_filters if use_filters else None
                )
                search_strategy = "semantic_with_filters" if use_filters else "semantic"

            # Formatear contexto para el prompt
            context = self._format_context_for_prompt(search_results)
            # Extraer información de fuente
            source_info = self._extract_source_info(search_results)
            # Enriquecer la respuesta correlacionando entidades con metadatos
            enriched_metadata = self._correlate_entities_with_metadata(entities, search_results)
            # Generar respuesta con Gemini
            response = self._generate_response_with_gemini(context, query, source_info, enriched_metadata)

            result = {
                "query": query,
                "response": response,
                "entities": entities,
                "filters_used": filters,
                "search_results_count": search_results.get('total_results', 0),
                "source_info": source_info,
                "enriched_metadata": enriched_metadata,
                "search_strategy": search_strategy,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Consulta procesada exitosamente: {query} (estrategia: {search_strategy})")
            return result
        except Exception as e:
            logger.error(f"Error procesando consulta '{query}': {e}")
            return {
                "query": query,
                "response": f"Error procesando la consulta: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _correlate_entities_with_metadata(self, entities: dict, search_results: dict) -> list:
        """Correlaciona entidades extraídas con los metadatos de los resultados encontrados."""
        try:
            results = search_results.get('results', {})
            metadatas = results.get('metadatas', [[]])
            enriched = []
            if not metadatas or not metadatas[0]:
                return enriched
            for meta in metadatas[0]:
                match = {}
                for ent_type, ent_list in entities.items():
                    if not ent_list:
                        continue
                    for ent in ent_list:
                        for k, v in meta.items():
                            if isinstance(v, str) and ent.lower() in v.lower():
                                match.setdefault(ent_type, []).append({"entity": ent, "metadata_field": k, "value": v})
                if match:
                    enriched.append({"metadata": meta, "matches": match})
            return enriched
        except Exception as e:
            logger.error(f"Error correlacionando entidades con metadatos: {e}")
            return []

    def _generate_response_with_gemini(self, context: str, query: str, source_info: Dict[str, any], enriched_metadata: list = None) -> str:
        """Generar respuesta usando Gemini, enriqueciendo con metadatos correlacionados si existen."""
        try:
            prompt = self.prompt_template.format(
                context=context,
                query=query
            )
            response = self.model.generate_content(prompt)
            document_id = source_info.get('document_id', 'unknown')
            chunk_position = source_info.get('chunk_position', 0)
            total_chunks = source_info.get('total_chunks', 0)
            source_text = f"\n\nFuente: {document_id}, Chunk {chunk_position} de {total_chunks}"
            # Añadir metadatos correlacionados si existen
            if enriched_metadata:
                meta_texts = []
                for item in enriched_metadata:
                    meta = item["metadata"]
                    matches = item["matches"]
                    meta_texts.append(f"Metadatos relevantes: {meta}\nCoincidencias: {matches}")
                source_text += "\n" + "\n".join(meta_texts)
            return response.text + source_text
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {e}")
            return f"Error generando respuesta: {str(e)}"
    
    def handle_batch_queries(self, queries: List[str]) -> List[Dict[str, any]]:
        """Manejar múltiples consultas"""
        results = []
        
        for query in queries:
            result = self.handle_query(query)
            results.append(result)
        
        return results 

    def _create_name_filters(self, names: List[str]) -> Dict[str, any]:
        """
        Crear filtros de ChromaDB para buscar nombres específicos en metadatos
        """
        try:
            if not names:
                return {}
            
            # Crear filtros OR para buscar nombres en diferentes campos de metadatos
            name_filters = []
            
            for name in names:
                # Normalizar el nombre para búsqueda
                normalized_name = name.upper().strip()
                
                # Buscar en campos que pueden contener nombres
                name_fields = [
                    'demandado', 'demandante', 'ejecutado', 'contribuyente',
                    'demandado_normalized', 'demandante_normalized', 'ejecutado_normalized',
                    # Campos de demandados extraídos del CSV
                    'demandados_0_nombre_apellidos_razon_social',
                    'demandados_1_nombre_apellidos_razon_social', 
                    'demandados_2_nombre_apellidos_razon_social',
                    'demandados_3_nombre_apellidos_razon_social',
                    'demandados_4_nombre_apellidos_razon_social',
                    'demandados_5_nombre_apellidos_razon_social',
                    'demandados_6_nombre_apellidos_razon_social',
                    'demandados_7_nombre_apellidos_razon_social',
                    'demandados_8_nombre_apellidos_razon_social',
                    'demandados_9_nombre_apellidos_razon_social'
                ]
                
                # Crear filtros OR para cada campo
                field_filters = []
                for field in name_fields:
                    field_filters.append({
                        field: {"$eq": normalized_name}
                    })
                
                # Agregar filtro OR para este nombre
                if field_filters:
                    name_filters.append({"$or": field_filters})
            
            # Combinar todos los nombres con AND
            if len(name_filters) == 1:
                return name_filters[0]
            elif len(name_filters) > 1:
                return {"$and": name_filters}
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error creando filtros de nombres: {e}")
            return {} 

    def _filter_results_by_name_substring(self, results: Dict, search_name: str) -> List[Dict]:
        """
        Filtrar resultados por coincidencia parcial de nombre en metadatos
        """
        try:
            if not results.get('results', {}).get('metadatas', [[]])[0]:
                return []
            
            metadatas = results['results']['metadatas'][0]
            documents = results['results']['documents'][0]
            distances = results['results']['distances'][0]
            
            filtered_results = []
            search_name_upper = search_name.upper().strip()
            
            # Campos donde buscar nombres
            name_fields = [
                'demandado', 'demandante', 'ejecutado', 'contribuyente',
                'demandado_normalized', 'demandante_normalized', 'ejecutado_normalized',
                # Campos de demandados extraídos del CSV
                'demandados_0_nombre_apellidos_razon_social',
                'demandados_1_nombre_apellidos_razon_social', 
                'demandados_2_nombre_apellidos_razon_social',
                'demandados_3_nombre_apellidos_razon_social',
                'demandados_4_nombre_apellidos_razon_social',
                'demandados_5_nombre_apellidos_razon_social',
                'demandados_6_nombre_apellidos_razon_social',
                'demandados_7_nombre_apellidos_razon_social',
                'demandados_8_nombre_apellidos_razon_social',
                'demandados_9_nombre_apellidos_razon_social'
            ]
            
            for i, metadata in enumerate(metadatas):
                # Buscar en todos los campos de nombres
                for field in name_fields:
                    field_value = metadata.get(field, '')
                    if field_value and search_name_upper in str(field_value).upper():
                        filtered_results.append({
                            'document_id': metadata.get('document_id', 'N/A'),
                            'score': 1.0 - distances[i] if i < len(distances) else 0.0,
                            'metadata': metadata,
                            'content': documents[i] if i < len(documents) else '',
                            'matched_field': field,
                            'matched_value': field_value
                        })
                        break  # Solo agregar una vez por chunk
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error filtrando resultados por substring: {e}")
            return [] 