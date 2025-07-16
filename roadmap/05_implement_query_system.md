# 05. Implementación del Sistema de Consultas - MVP RAG

## 🎯 Objetivo
Implementar el sistema de consultas con integración de Gemini 2.0 Flash Lite, extracción de filtros mejorada, búsqueda híbrida y trazabilidad de respuestas.

## 📋 Tareas a Ejecutar

### 1. Crear Módulo de Consultas
Crear `src/query/query_handler.py`:
```python
"""
Módulo para manejo de consultas con Gemini y trazabilidad
"""
import google.generativeai as genai
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from config.settings import GOOGLE_API_KEY, GOOGLE_MODEL
from src.indexing.chroma_indexer import ChromaIndexer
from src.utils.text_utils import normalize_text, extract_legal_entities
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/query.log")

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
- Al final de cada respuesta, incluye: "Fuente: {document_id}, Chunk {chunk_position} de {total_chunks}"

Tareas posibles:
- Resumir el contenido legal
- Responder preguntas específicas del contenido
- Extraer campos clave como fechas, cuantías o nombres
- Identificar tipos de medidas cautelares

Respuesta:
"""
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, any]:
        """Extraer filtros de la consulta con normalización"""
        filters = {}
        
        # Normalizar consulta
        normalized_query = normalize_text(query)
        
        # Extraer entidades legales
        entities = extract_legal_entities(query)
        
        # Mapear entidades a filtros
        if entities['names']:
            # Usar el primer nombre encontrado como demandante
            filters['demandante_normalized'] = normalize_text(entities['names'][0])
        
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
        
        return filters
    
    def _format_context_for_prompt(self, search_results: Dict[str, any]) -> str:
        """Formatear contexto para el prompt"""
        if 'error' in search_results:
            return "No se encontraron documentos relevantes para la consulta."
        
        context_parts = []
        results = search_results['results']
        
        if not results['documents']:
            return "No se encontraron documentos relevantes para la consulta."
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            # Extraer información de fuente
            document_id = metadata.get('document_id', 'unknown')
            chunk_position = metadata.get('chunk_position', 0)
            total_chunks = metadata.get('total_chunks', 0)
            
            # Formatear chunk
            chunk_text = doc[:500] + "..." if len(doc) > 500 else doc
            chunk_info = f"[Chunk {chunk_position}/{total_chunks} del documento {document_id}]"
            
            context_parts.append(f"{chunk_info}\n{chunk_text}")
        
        return "\n\n".join(context_parts)
    
    def _extract_source_info(self, search_results: Dict[str, any]) -> Dict[str, any]:
        """Extraer información de fuente de los resultados"""
        if 'error' in search_results or not search_results['results']['metadatas']:
            return {"document_id": "unknown", "chunk_position": 0, "total_chunks": 0}
        
        # Usar el primer resultado como fuente principal
        first_metadata = search_results['results']['metadatas'][0][0]
        
        return {
            "document_id": first_metadata.get('document_id', 'unknown'),
            "chunk_position": first_metadata.get('chunk_position', 0),
            "total_chunks": first_metadata.get('total_chunks', 0)
        }
    
    def _generate_response_with_gemini(self, context: str, query: str, source_info: Dict[str, any]) -> str:
        """Generar respuesta usando Gemini"""
        try:
            # Construir prompt completo
            prompt = self.prompt_template.format(
                context=context,
                query=query
            )
            
            # Generar respuesta
            response = self.model.generate_content(prompt)
            
            # Añadir información de fuente
            source_text = f"\n\nFuente: {source_info['document_id']}, Chunk {source_info['chunk_position']} de {source_info['total_chunks']}"
            
            return response.text + source_text
            
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {e}")
            return f"Error generando respuesta: {str(e)}"
    
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
            # Extraer filtros de la consulta
            filters = self._extract_filters_from_query(query)
            logger.info(f"Filtros extraídos: {filters}")
            
            # Realizar búsqueda híbrida
            search_results = self.indexer.search_similar(
                query=query,
                n_results=n_results,
                where=filters if filters else None
            )
            
            # Formatear contexto para el prompt
            context = self._format_context_for_prompt(search_results)
            
            # Extraer información de fuente
            source_info = self._extract_source_info(search_results)
            
            # Generar respuesta con Gemini
            response = self._generate_response_with_gemini(context, query, source_info)
            
            result = {
                "query": query,
                "response": response,
                "filters_used": filters,
                "search_results_count": search_results.get('total_found', 0),
                "source_info": source_info,
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
    
    def handle_batch_queries(self, queries: List[str]) -> List[Dict[str, any]]:
        """Manejar múltiples consultas"""
        results = []
        
        for query in queries:
            result = self.handle_query(query)
            results.append(result)
        
        return results
```

### 2. Crear Módulo de Extracción de Filtros Mejorado
Crear `src/query/filter_extractor.py`:
```python
"""
Módulo mejorado para extracción de filtros de consultas
"""
import re
from typing import Dict, List, Optional
from src.utils.text_utils import normalize_text, extract_legal_entities

class FilterExtractor:
    def __init__(self):
        # Patrones específicos para consultas legales
        self.patterns = {
            'demandante': [
                r'(?:demandante|actor|solicitante)\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ\s]+)',
                r'(?:el\s+)?demandante\s+([A-ZÁÉÍÓÚÑ\s]+)',
                r'([A-ZÁÉÍÓÚÑ\s]+)\s+(?:es\s+el\s+)?demandante'
            ],
            'demandado': [
                r'(?:demandado|demandada|entidad)\s+(?:es\s+)?([A-ZÁÉÍÓÚÑ\s]+)',
                r'(?:el\s+)?demandado\s+([A-ZÁÉÍÓÚÑ\s]+)',
                r'([A-ZÁÉÍÓÚÑ\s]+)\s+(?:es\s+el\s+)?demandado'
            ],
            'cuantia': [
                r'(?:cuantía|monto|valor)\s+(?:es\s+)?(\$?[\d,\.]+)',
                r'(\$?[\d,\.]+)\s+(?:es\s+la\s+)?cuantía',
                r'por\s+(\$?[\d,\.]+)'
            ],
            'fecha': [
                r'(?:fecha|día)\s+(?:es\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(?:es\s+la\s+)?fecha',
                r'el\s+(\d{1,2}\s+de\s+[a-z]+\s+de\s+\d{4})'
            ],
            'tipo_medida': [
                r'(?:tipo\s+de\s+)?medida\s+(?:es\s+)?([a-záéíóúñ\s]+)',
                r'([a-záéíóúñ\s]+)\s+(?:es\s+el\s+)?tipo\s+de\s+medida',
                r'(embargo|medida\s+cautelar|secuestro|prohibición)'
            ]
        }
        
        # Términos de medida mapeados
        self.measure_mapping = {
            'embargo': 'Embargo',
            'medida cautelar': 'Medida Cautelar',
            'secuestro': 'Secuestro',
            'prohibición': 'Prohibición',
            'suspensión': 'Suspensión'
        }
    
    def extract_filters(self, query: str) -> Dict[str, any]:
        """Extraer filtros de la consulta"""
        filters = {}
        
        # Normalizar consulta
        normalized_query = normalize_text(query)
        
        # Extraer entidades legales
        entities = extract_legal_entities(query)
        
        # Procesar cada tipo de filtro
        for filter_type, patterns in self.patterns.items():
            value = self._extract_with_patterns(query, patterns)
            
            if value:
                if filter_type == 'demandante':
                    filters['demandante_normalized'] = normalize_text(value)
                elif filter_type == 'demandado':
                    filters['demandado_normalized'] = normalize_text(value)
                elif filter_type == 'cuantia':
                    amount_clean = ''.join(filter(str.isdigit, value))
                    filters['cuantia_normalized'] = amount_clean
                elif filter_type == 'fecha':
                    filters['fecha_normalized'] = value
                elif filter_type == 'tipo_medida':
                    normalized_measure = normalize_text(value)
                    for key, mapped_value in self.measure_mapping.items():
                        if key in normalized_measure:
                            filters['tipo_medida'] = mapped_value
                            break
        
        # Usar entidades extraídas como respaldo
        if not filters.get('demandante_normalized') and entities['names']:
            filters['demandante_normalized'] = normalize_text(entities['names'][0])
        
        if not filters.get('cuantia_normalized') and entities['amounts']:
            amount_clean = ''.join(filter(str.isdigit, entities['amounts'][0]))
            filters['cuantia_normalized'] = amount_clean
        
        if not filters.get('fecha_normalized') and entities['dates']:
            filters['fecha_normalized'] = entities['dates'][0]
        
        return filters
    
    def _extract_with_patterns(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extraer valor usando múltiples patrones"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        return None
    
    def validate_filters(self, filters: Dict[str, any]) -> Dict[str, any]:
        """Validar y limpiar filtros"""
        validated = {}
        
        for key, value in filters.items():
            if value and str(value).strip():
                # Limpiar espacios extra
                cleaned_value = str(value).strip()
                
                # Validaciones específicas
                if 'normalized' in key:
                    # Asegurar que esté normalizado
                    cleaned_value = normalize_text(cleaned_value)
                
                validated[key] = cleaned_value
        
        return validated
```

### 3. Crear Script de Consultas Interactivo
Crear `scripts/interactive_query.py`:
```python
#!/usr/bin/env python3
"""
Script interactivo para probar consultas
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.query.query_handler import QueryHandler
from src.query.filter_extractor import FilterExtractor

def main():
    print("🤖 Sistema de Consultas RAG - Modo Interactivo")
    print("=" * 50)
    print("Escribe 'salir' para terminar")
    print("Escribe 'ayuda' para ver ejemplos de consultas")
    print()
    
    # Inicializar componentes
    query_handler = QueryHandler()
    filter_extractor = FilterExtractor()
    
    # Ejemplos de consultas
    examples = [
        "¿Cuál es el demandante del expediente?",
        "¿Qué tipo de medida se solicitó?",
        "¿Cuál es la cuantía del embargo?",
        "Resume el expediente RCCI2150725310",
        "¿Cuáles son los hechos principales?",
        "embargos de Nury Romero"
    ]
    
    while True:
        try:
            # Obtener consulta del usuario
            query = input("\n🔍 Tu consulta: ").strip()
            
            if query.lower() == 'salir':
                print("👋 ¡Hasta luego!")
                break
            
            if query.lower() == 'ayuda':
                print("\n📝 Ejemplos de consultas:")
                for i, example in enumerate(examples, 1):
                    print(f"   {i}. {example}")
                continue
            
            if not query:
                print("❌ Por favor, ingresa una consulta válida")
                continue
            
            print(f"\n🔄 Procesando: {query}")
            
            # Extraer filtros (para debug)
            filters = filter_extractor.extract_filters(query)
            validated_filters = filter_extractor.validate_filters(filters)
            
            if validated_filters:
                print(f"🔍 Filtros detectados: {validated_filters}")
            
            # Procesar consulta
            result = query_handler.handle_query(query)
            
            # Mostrar respuesta
            print(f"\n💬 Respuesta:")
            print("-" * 40)
            print(result['response'])
            print("-" * 40)
            
            # Mostrar información adicional
            print(f"\n📊 Información:")
            print(f"   - Resultados encontrados: {result['search_results_count']}")
            print(f"   - Fuente: {result['source_info']['document_id']}")
            print(f"   - Chunk: {result['source_info']['chunk_position']}/{result['source_info']['total_chunks']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

### 4. Crear Tests Unitarios
Crear `tests/unit/test_query_system.py`:
```python
"""
Tests unitarios para el sistema de consultas
"""
import pytest
from unittest.mock import Mock, patch
from src.query.query_handler import QueryHandler
from src.query.filter_extractor import FilterExtractor

class TestQueryHandler:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                self.query_handler = QueryHandler()
    
    def test_extract_filters_from_query(self):
        """Test de extracción de filtros"""
        query = "¿Cuál es el demandante Juan Pérez?"
        filters = self.query_handler._extract_filters_from_query(query)
        
        assert 'demandante_normalized' in filters
        assert filters['demandante_normalized'] == 'juan perez'
    
    def test_extract_filters_with_amount(self):
        """Test de extracción de filtros con cuantía"""
        query = "¿Cuál es la cuantía de $1,000,000?"
        filters = self.query_handler._extract_filters_from_query(query)
        
        assert 'cuantia_normalized' in filters
        assert filters['cuantia_normalized'] == '1000000'
    
    def test_extract_filters_with_date(self):
        """Test de extracción de filtros con fecha"""
        query = "¿Cuál es la fecha del 15/01/2024?"
        filters = self.query_handler._extract_filters_from_query(query)
        
        assert 'fecha_normalized' in filters
        assert filters['fecha_normalized'] == '15/01/2024'
    
    def test_format_context_for_prompt(self):
        """Test de formateo de contexto"""
        search_results = {
            'results': {
                'documents': [['Texto de prueba del chunk 1']],
                'metadatas': [[{
                    'document_id': 'test_doc',
                    'chunk_position': 1,
                    'total_chunks': 3
                }]]
            }
        }
        
        context = self.query_handler._format_context_for_prompt(search_results)
        
        assert 'test_doc' in context
        assert 'Chunk 1/3' in context
        assert 'Texto de prueba' in context
    
    def test_extract_source_info(self):
        """Test de extracción de información de fuente"""
        search_results = {
            'results': {
                'metadatas': [[{
                    'document_id': 'test_doc',
                    'chunk_position': 2,
                    'total_chunks': 5
                }]]
            }
        }
        
        source_info = self.query_handler._extract_source_info(search_results)
        
        assert source_info['document_id'] == 'test_doc'
        assert source_info['chunk_position'] == 2
        assert source_info['total_chunks'] == 5

class TestFilterExtractor:
    
    def setup_method(self):
        """Configurar antes de cada test"""
        self.extractor = FilterExtractor()
    
    def test_extract_demandante(self):
        """Test de extracción de demandante"""
        query = "El demandante es Juan Pérez"
        filters = self.extractor.extract_filters(query)
        
        assert 'demandante_normalized' in filters
        assert filters['demandante_normalized'] == 'juan perez'
    
    def test_extract_cuantia(self):
        """Test de extracción de cuantía"""
        query = "La cuantía es $500,000"
        filters = self.extractor.extract_filters(query)
        
        assert 'cuantia_normalized' in filters
        assert filters['cuantia_normalized'] == '500000'
    
    def test_extract_tipo_medida(self):
        """Test de extracción de tipo de medida"""
        query = "El tipo de medida es embargo"
        filters = self.extractor.extract_filters(query)
        
        assert 'tipo_medida' in filters
        assert filters['tipo_medida'] == 'Embargo'
    
    def test_validate_filters(self):
        """Test de validación de filtros"""
        filters = {
            'demandante_normalized': '  JUAN PÉREZ  ',
            'cuantia_normalized': '1000000',
            'empty_filter': ''
        }
        
        validated = self.extractor.validate_filters(filters)
        
        assert 'demandante_normalized' in validated
        assert validated['demandante_normalized'] == 'juan perez'
        assert 'cuantia_normalized' in validated
        assert 'empty_filter' not in validated
```

### 5. Crear Script de Evaluación
Crear `scripts/evaluate_queries.py`:
```python
#!/usr/bin/env python3
"""
Script para evaluar consultas con preguntas de prueba
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.query.query_handler import QueryHandler

def main():
    print("📊 Evaluación del Sistema de Consultas")
    print("=" * 50)
    
    # Consultas de prueba
    test_queries = [
        "¿Cuál es el demandante del expediente?",
        "¿Qué tipo de medida se solicitó?",
        "¿Cuál es la cuantía del embargo?",
        "¿En qué fecha se dictó la medida?",
        "¿Cuáles son los hechos principales del caso?",
        "¿Qué fundamentos jurídicos se esgrimen?",
        "¿Cuáles son las medidas cautelares solicitadas?",
        "Resume el expediente",
        "¿Cuál es el estado actual del proceso?",
        "¿Quién es el juez del caso?"
    ]
    
    # Inicializar query handler
    query_handler = QueryHandler()
    
    results = []
    
    print(f"🧪 Evaluando {len(test_queries)} consultas...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Procesando: {query}")
        
        try:
            result = query_handler.handle_query(query)
            
            # Evaluar calidad de respuesta
            quality_score = evaluate_response_quality(result['response'])
            
            result['quality_score'] = quality_score
            results.append(result)
            
            print(f"   ✅ Completado - Calidad: {quality_score}/5")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'query': query,
                'error': str(e),
                'quality_score': 0
            })
    
    # Calcular estadísticas
    successful = len([r for r in results if 'error' not in r])
    avg_quality = sum(r['quality_score'] for r in results) / len(results)
    
    print(f"\n📊 Resultados de Evaluación:")
    print(f"   - Consultas exitosas: {successful}/{len(test_queries)}")
    print(f"   - Calidad promedio: {avg_quality:.2f}/5")
    print(f"   - Tasa de éxito: {(successful/len(test_queries))*100:.1f}%")
    
    # Guardar resultados
    with open("logs/query_evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en logs/query_evaluation_results.json")

def evaluate_response_quality(response: str) -> int:
    """Evaluar calidad de respuesta (1-5)"""
    if not response or "Error" in response:
        return 1
    
    # Criterios de calidad
    score = 0
    
    # Respuesta no vacía
    if len(response) > 10:
        score += 1
    
    # Incluye información específica
    if any(keyword in response.lower() for keyword in ['demandante', 'demandado', 'embargo', 'medida']):
        score += 1
    
    # Incluye fuente
    if 'Fuente:' in response:
        score += 1
    
    # Respuesta coherente
    if not response.startswith("No se encuentra"):
        score += 1
    
    # Respuesta completa
    if len(response) > 50:
        score += 1
    
    return score

if __name__ == "__main__":
    main()
```

## ✅ Criterios de Éxito
- [ ] Módulo `QueryHandler` implementado correctamente
- [ ] Extracción de filtros mejorada funcionando
- [ ] Integración con Gemini funcionando
- [ ] Trazabilidad en respuestas implementada
- [ ] Búsqueda híbrida operativa
- [ ] Tests unitarios pasando
- [ ] Script interactivo funcionando

## 🔍 Verificación
Ejecutar los siguientes comandos:
```bash
# Probar consultas interactivas
python scripts/interactive_query.py

# Evaluar consultas
python scripts/evaluate_queries.py

# Ejecutar tests
python -m pytest tests/unit/test_query_system.py -v

# Verificar logs
cat logs/query.log
```

## 📊 Métricas de Calidad
- **Tasa de éxito de consultas**: > 80%
- **Calidad promedio de respuestas**: > 3.5/5
- **Trazabilidad**: 100% de respuestas con fuente
- **Tiempo de respuesta**: < 5 segundos por consulta

## 📝 Notas Importantes
- La extracción de filtros debe ser robusta y tolerante a variaciones
- Las respuestas deben incluir siempre información de fuente
- El prompt estructurado es crítico para respuestas consistentes
- La evaluación debe ejecutarse regularmente para monitorear calidad 