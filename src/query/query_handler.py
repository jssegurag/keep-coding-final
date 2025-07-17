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
        """Extraer filtros de la consulta con normalización"""
        filters = {}
        
        # Normalizar consulta
        normalized_query = normalize_text(query)
        
        # Extraer entidades legales
        entities = extract_legal_entities(query)
        
        # Mapear entidades a filtros usando los campos normalizados existentes
        if entities['names']:
            # Filtrar nombres válidos (excluir palabras comunes)
            valid_names = [name for name in entities['names'] if len(name.strip()) > 2 and name.strip().lower() not in ['que', 'es', 'un', 'una', 'del', 'de', 'la', 'el', 'expediente', 'demandante', 'cuál', 'cual', 'información', 'tienes', 'hay']]
            if valid_names:
                # Solo usar filtros para nombres muy específicos (no para consultas generales)
                name = valid_names[0].lower()
                # Excluir palabras comunes y términos de consulta
                excluded_terms = ['coordinadora', 'comercial', 'cargas', 'ccc', 'sa', 'información', 'tienes', 'hay', 'de']
                if name not in excluded_terms and len(name) > 3:
                    filters['demandante_normalized'] = normalize_text(valid_names[0])
        
        if entities['dates']:
            # Usar la primera fecha encontrada
            filters['fecha_normalized'] = entities['dates'][0]
        
        if entities['amounts']:
            # Usar la primera cantidad encontrada
            amount_clean = ''.join(filter(str.isdigit, entities['amounts'][0]))
            filters['cuantia_normalized'] = amount_clean
        
        # Detectar tipos de medida
        legal_terms = entities['legal_terms']
        if 'embargo' in legal_terms:
            filters['tipo_medida'] = 'Embargo'
        elif 'medida cautelar' in legal_terms:
            filters['tipo_medida'] = 'Medida Cautelar'
        
        # Extraer números de expediente
        if entities['document_numbers']:
            filters['document_id'] = entities['document_numbers'][0]
        
        # Patrones específicos para consultas comunes
        patterns = {
            'demandante': r'(?:demandante|actor|solicitante)\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ\s]+)',
            'demandado': r'(?:demandado|demandada|entidad)\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ\s]+)',
            'cuantia': r'(?:cuantía|monto|valor)\s+(?:es\s+)?(\$?[\d,\.]+)',
            'fecha': r'(?:fecha|día)\s+(?:es\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        }
        
        for filter_key, pattern in patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                if filter_key == 'demandante':
                    filters['demandante_normalized'] = normalize_text(matches[0])
                elif filter_key == 'demandado':
                    filters['demandado_normalized'] = normalize_text(matches[0])
                elif filter_key == 'cuantia':
                    amount_clean = ''.join(filter(str.isdigit, matches[0]))
                    filters['cuantia_normalized'] = amount_clean
                elif filter_key == 'fecha':
                    filters['fecha_normalized'] = matches[0]
        
        # Si no se encontraron filtros útiles, limpiar filtros
        if filters:
            # Verificar que los filtros no sean solo palabras comunes
            common_words = ['que', 'es', 'un', 'una', 'del', 'de', 'la', 'el', 'expediente', 'demandante', 'cuál', 'cual', 'del expediente']
            filtered_filters = {}
            for key, value in filters.items():
                if value and value.lower() not in common_words:
                    filtered_filters[key] = value
            filters = filtered_filters
        
        return filters
    
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
        Manejar consulta completa
        Args:
            query: Consulta del usuario
            n_results: Número de resultados a buscar
        Returns:
            Respuesta estructurada
        """
        logger.info(f"Procesando consulta: {query}")
        try:
            # Extraer entidades de la consulta (pero NO usar como filtro)
            entities = extract_legal_entities(query)
            filters = self._extract_filters_from_query(query)  # Solo para casos estructurados
            logger.info(f"Entidades extraídas: {entities}")
            logger.info(f"Filtros extraídos: {filters}")

            # Solo usar filtros para casos muy específicos (fechas, cuantías, números de expediente)
            # NO usar filtros para términos generales como "embargo", "medida cautelar", etc.
            chromadb_filters = self._convert_filters_to_chromadb_format(filters)
            use_filters = False
            
            if chromadb_filters:
                # Solo usar filtros muy específicos, no términos generales
                specific_filters = ['fecha_normalized', 'cuantia_normalized', 'document_id']
                if any(key in chromadb_filters for key in specific_filters):
                    # Excluir filtros de nombres y términos generales
                    if 'demandante_normalized' in chromadb_filters:
                        del chromadb_filters['demandante_normalized']
                    if 'tipo_medida' in chromadb_filters:
                        del chromadb_filters['tipo_medida']
                    if chromadb_filters:  # Solo usar si quedan filtros específicos
                        use_filters = True

            # Búsqueda SIEMPRE semántica sin filtros restrictivos
            search_results = self.indexer.search_similar(
                query=query,
                n_results=n_results,
                where=chromadb_filters if use_filters else None
            )

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
                "filters_used": filters if use_filters else {},
                "search_results_count": search_results.get('total_found', 0),
                "source_info": source_info,
                "enriched_metadata": enriched_metadata,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Consulta procesada exitosamente: {query}")
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