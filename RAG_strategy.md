# Estrategia RAG para Sistema de Expedientes Jurídicos - MVP Blindado

## 1. Arquitectura de Indexación - MVP Blindado

### 1.1 Stack Tecnológico para MVP

**Arquitectura Simplificada: ChromaDB + SQLite + Gemini 2.0 Flash Lite**

#### Componentes Principales:
- **ChromaDB**: Base de datos vectorial + metadatos filtrables
- **SQLite**: Base de datos relacional para metadatos canónicos
- **Gemini 2.0 Flash Lite**: LLM para generación de respuestas

#### Justificación de la Simplificación:

1. **Eliminación de Complejidad Innecesaria**: 
   - Un solo motor de búsqueda vectorial con filtrado nativo
   - Sin enrutamiento complejo de consultas
   - Flujo único y robusto

2. **Optimización para MVP**: 
   - ChromaDB maneja tanto vectores como filtrado de metadatos
   - SQLite solo para datos de referencia
   - Respuestas rápidas y precisas

3. **Escalabilidad Futura**: 
   - Fácil migración a arquitectura híbrida completa
   - Base sólida para iteraciones

### 1.2 Estrategia de Chunking - CRÍTICA PARA MVP

#### Implementación Obligatoria de Chunking:

**Problema Identificado**: Un embedding por documento completo es inútil para RAG efectivo.

**Solución MVP**:
- **Tamaño de Chunk**: 512 tokens con overlap de 50 tokens
- **Estrategia**: División por párrafos naturales + límite de tokens
- **Metadatos por Chunk**: ID documento padre + posición + metadatos relevantes

#### Estructura de Chunking:
```
Documento RCCI2150725310
├── Chunk 1: [0-512 tokens] - Encabezado y datos básicos
├── Chunk 2: [462-974 tokens] - Demandante y demandado
├── Chunk 3: [924-1436 tokens] - Hechos principales
├── Chunk 4: [1386-1898 tokens] - Medidas cautelares
└── Chunk N: [últimos tokens] - Firmas y conclusiones
```

#### Metadatos por Chunk:
```json
{
  "document_id": "RCCI2150725310",
  "chunk_id": "RCCI2150725310_chunk_1",
  "chunk_position": 1,
  "total_chunks": 5,
  "demandante": "NURY WILLELMA ROMERO GOMEZ",
  "demandado": "MUNICIPIO DE ARAUCA",
  "tipo_medida": "Embargo",
  "entidad": "MUNICIPIO DE ARAUCA",
  "fecha": "2025-07-14",
  "cuantia": "238.984.000,00"
}
```

### 1.3 Flujo de Consulta Simplificado - MVP

#### Eliminación del Enrutador Complejo:

**Problema Identificado**: Clasificación de consultas añade complejidad innecesaria.

**Solución MVP - Flujo Único**:
1. **Extracción de Filtros**: Extraer entidades de la consulta (nombres, fechas, números)
2. **Búsqueda Híbrida Simplificada**:
   - Filtrar chunks en ChromaDB por metadatos
   - Búsqueda vectorial en chunks filtrados
3. **Recuperación de Contexto**: Top-k chunks más relevantes
4. **Generación con LLM**: Prompt único que maneja todos los tipos de consulta

#### Prompt Único para Gemini con Instrucciones Estructuradas:
```
Contexto: {chunks_recuperados}

Pregunta del usuario: {consulta_original}

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
```

## 2. Flujo de Datos Simplificado - MVP

### 2.1 Proceso de Ingesta con Chunking

#### Fase 1: Extracción y Chunking
1. **Lectura de Datos**
   - Leer CSV de metadatos
   - Extraer texto completo de JSON de Docling
   - Parsear metadatos estructurados

2. **Chunking Obligatorio**
   - Dividir texto en chunks de 512 tokens
   - Overlap de 50 tokens entre chunks
   - Preservar estructura semántica (párrafos)
   - **Fallback recursivo**: Si un párrafo excede 512 tokens, dividir por oraciones

3. **Preparación de Metadatos**
   - Asignar metadatos a cada chunk
   - Generar IDs únicos por chunk
   - Validar integridad de datos

#### Fase 2: Indexación Simplificada
1. **Indexación en ChromaDB**
   - Generar embedding por chunk
   - Almacenar metadatos filtrables
   - Asociar con ID del documento padre

2. **Base de Datos de Referencia**
   - SQLite solo para metadatos canónicos
   - Relaciones documento-chunks
   - Estadísticas de indexación

### 2.2 Flujo de Consulta - MVP Blindado

#### Eliminación del Enrutador:
**Antes (Complejo)**:
```
Consulta → Clasificador → Enrutador → Motor específico → Respuesta
```

**Ahora (Simple)**:
```
Consulta → Extracción filtros → Búsqueda híbrida → LLM → Respuesta
```

#### Proceso Detallado:

1. **Extracción de Filtros Mejorada**
   - **Normalización de nombres**: Convertir a minúscula, sin tildes
   - **Búsqueda parcial**: Usar LIKE para nombres similares
   - **Patrones de fechas**: Detectar formatos DD/MM/YYYY, YYYY-MM-DD
   - **Números y cuantías**: Extraer valores monetarios
   - **Términos jurídicos**: Detectar tipos de medidas cautelares

2. **Búsqueda Híbrida en ChromaDB**
   ```python
   # Pseudocódigo con tolerancia mejorada
   normalized_filters = normalize_filters(extracted_filters)
   filtered_chunks = chroma_collection.query(
       query_texts=[user_query],
       where=normalized_filters,
       n_results=10
   )
   ```

3. **Generación con Gemini**
   - Construir prompt con contexto y instrucciones estructuradas
   - Dejar que Gemini interprete la intención
   - Generar respuesta apropiada con trazabilidad

## 3. Especificaciones de Diseño - MVP Blindado

### 3.1 Estructura de Datos Simplificada

#### Chunk en ChromaDB:
```json
{
  "id": "RCCI2150725310_chunk_1",
  "embedding": [vector_512_dimensions],
  "text": "Texto del chunk...",
  "metadata": {
    "document_id": "RCCI2150725310",
    "chunk_position": 1,
    "demandante": "NURY WILLELMA ROMERO GOMEZ",
    "demandado": "MUNICIPIO DE ARAUCA",
    "tipo_medida": "Embargo",
    "entidad": "MUNICIPIO DE ARAUCA",
    "fecha": "2025-07-14",
    "cuantia": "238.984.000,00",
    "demandante_normalized": "nury willelma romero gomez",
    "demandado_normalized": "municipio de arauca"
  }
}
```

#### Documento en SQLite (Referencia):
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT,
    total_chunks INTEGER,
    indexed_at TIMESTAMP,
    metadata_json TEXT
);
```

### 3.2 Configuración de Búsqueda - MVP Blindado

#### ChromaDB:
- **Dimensiones**: 512 (sentence-transformers)
- **Distancia**: Coseno
- **Filtrado**: Metadatos nativos con normalización
- **Resultados**: Top-10 chunks

#### SQLite:
- **Búsqueda**: Solo para estadísticas
- **Relaciones**: Documento-chunks
- **Backup**: Metadatos canónicos

## 4. Validación y Testing - MVP Blindado

### 4.1 Validación de Embeddings para Textos Legales

#### Prueba Previa de Embeddings:
**Antes de indexar todo el corpus**:
1. **Seleccionar 5 documentos representativos** con diferentes tipos de contenido legal
2. **Crear 10 preguntas de prueba** que cubran diferentes aspectos (nombres, fechas, cuantías, tipos de medida)
3. **Generar embeddings** con `paraphrase-multilingual-mpnet-base-v2`
4. **Comparar resultados** con búsquedas manuales esperadas
5. **Si la precisión es < 70%**, considerar alternativas como `all-MiniLM-L6-v2` o `distiluse-base-multilingual-cased-v2`

#### Criterios de Validación:
- [ ] Embeddings capturan similitud semántica en textos legales
- [ ] Búsquedas por nombres devuelven resultados relevantes
- [ ] Búsquedas por conceptos jurídicos funcionan correctamente

### 4.2 Testing Unitario para Chunking y Búsqueda

#### Archivo de Testing: `run_test_set.py`
```python
# Pseudocódigo para testing
def test_chunking_and_search():
    # 1. Documentos de prueba
    test_docs = load_test_documents()
    
    # 2. Preguntas de prueba con respuestas esperadas
    test_questions = [
        ("¿Cuál es el demandante?", "NURY WILLELMA ROMERO GOMEZ"),
        ("¿Cuál es la cuantía?", "238.984.000,00"),
        ("¿Qué tipo de medida es?", "Embargo")
    ]
    
    # 3. Ejecutar chunking y búsqueda
    for doc in test_docs:
        chunks = chunk_document(doc)
        for question, expected in test_questions:
            result = search_and_answer(question, chunks)
            assert expected in result
```

#### Métricas de Testing:
- **Recall@k**: Medir cuántos chunks relevantes se recuperan
- **Precisión**: Verificar que los chunks recuperados contienen la información buscada
- **Tiempo de respuesta**: < 3 segundos por consulta

### 4.3 Evaluación Cualitativa con 20 Preguntas

#### Set de Preguntas Representativas:
1. **Preguntas de metadatos** (5 preguntas):
   - "¿Cuál es el demandante del expediente RCCI2150725310?"
   - "¿Cuál es la cuantía del embargo?"
   - "¿En qué fecha se dictó la medida?"

2. **Preguntas de contenido** (10 preguntas):
   - "¿Cuáles son los hechos principales del caso?"
   - "¿Qué fundamentos jurídicos se esgrimen?"
   - "¿Cuáles son las medidas cautelares solicitadas?"

3. **Preguntas de resumen** (5 preguntas):
   - "Resume el expediente RCCI2150725310"
   - "¿Cuál es el estado actual del proceso?"

#### Escala de Evaluación:
- **Correcta**: Respuesta precisa y completa
- **Parcialmente Correcta**: Respuesta con información relevante pero incompleta
- **Incorrecta**: Respuesta errónea o sin información útil

**Objetivo MVP**: > 80% de respuestas en categorías "Correcta" o "Parcialmente Correcta"

## 5. Plan de Implementación - MVP Blindado

### 5.1 Fase 1: Validación de Embeddings y Pipeline End-to-End

#### Objetivo Principal:
**Validar que el sistema RAG funciona de extremo a extremo con embeddings apropiados**

#### Tareas Críticas:

1. **Validación de Embeddings**
   - Probar `paraphrase-multilingual-mpnet-base-v2` con 5 documentos
   - Crear y ejecutar 10 preguntas de prueba
   - Si no funciona bien, probar alternativas

2. **Implementar Chunking con Fallback**
   - Función de división de texto en chunks
   - Preservación de metadatos por chunk
   - Fallback recursivo para chunks grandes
   - Validación de integridad

3. **Indexación en ChromaDB con Normalización**
   - Generación de embeddings por chunk
   - Almacenamiento con metadatos normalizados
   - Validación de indexación

4. **Flujo de Consulta Único con Trazabilidad**
   - Extracción de filtros mejorada
   - Búsqueda híbrida en ChromaDB
   - Integración con Gemini
   - Inclusión de fuente en respuestas

5. **Testing Unitario**
   - Implementar `run_test_set.py`
   - Validar chunking y búsqueda
   - Medir Recall@k y precisión

#### Criterios de Éxito Fase 1:
- [ ] Embeddings validados para textos legales
- [ ] Chunking funcional con fallback
- [ ] Búsqueda híbrida operativa
- [ ] Integración con Gemini funcionando
- [ ] Testing unitario pasando
- [ ] Trazabilidad en respuestas

### 5.2 Fase 2: Optimización y Evaluación Cualitativa

#### Objetivo:
**Mejorar precisión y validar con preguntas reales**

#### Tareas:
1. **Optimizar Chunking**
   - Ajustar tamaño de chunks basado en resultados
   - Mejorar estrategia de división
   - Optimizar overlap

2. **Mejorar Prompts**
   - Refinar prompt único con instrucciones estructuradas
   - Añadir ejemplos específicos para textos legales
   - Optimizar para diferentes tipos de consulta

3. **Evaluación Cualitativa**
   - Ejecutar 20 preguntas representativas
   - Evaluar respuestas según escala definida
   - Ajustar sistema basado en resultados

### 5.3 Fase 3: Escalabilidad y Monitoreo

#### Objetivo:
**Preparar para crecimiento y monitoreo**

#### Tareas:
1. **Monitoreo y Métricas**
   - Tiempo de respuesta
   - Precisión de respuestas
   - Uso de recursos

2. **Optimizaciones de Rendimiento**
   - Caché de consultas frecuentes
   - Compresión de embeddings
   - Indexación incremental

## 6. Configuración Rápida para MVP Blindado

### 6.1 Stack Final Recomendado

**Herramientas Seleccionadas:**
- **ChromaDB**: Base vectorial + filtrado de metadatos
- **SQLite**: Base de datos de referencia
- **Google Gemini 2.0 Flash Lite**: LLM económico
- **Sentence Transformers**: Embeddings de chunks

### 6.2 Instalación y Configuración

#### Dependencias:
```bash
pip install chromadb google-generativeai sentence-transformers pandas
```

#### Estructura de Archivos:
```
mvp/
├── data/
│   ├── chroma_db/          # ChromaDB automático
│   └── legal_docs.db       # SQLite reference
├── src/
│   ├── chunker.py          # Función de chunking con fallback
│   ├── indexer.py          # Indexador con normalización
│   ├── query_handler.py    # Manejador único con trazabilidad
│   ├── test_set.py         # Testing unitario
│   └── config.py
├── requirements.txt
└── run_mvp.py
```

#### Configuración Mínima:
```python
# config.py
GOOGLE_API_KEY = "tu-api-key"
CSV_PATH = "src/resources/metadata/studio_results_20250715_2237.csv"
TARGET_PATH = "target/"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
```

### 6.3 Implementación de Chunking con Fallback

#### Función Crítica:
```python
def chunk_document(text, metadata, chunk_size=512, overlap=50):
    """
    Divide el texto en chunks con metadatos preservados
    Incluye fallback recursivo para chunks grandes
    """
    # Implementar lógica de chunking
    # Preservar metadatos por chunk
    # Fallback recursivo por oraciones si es necesario
    # Generar IDs únicos
    pass
```

### 6.4 Flujo de Consulta Blindado

#### Pseudocódigo:
```python
def handle_query(query):
    # 1. Extraer filtros con normalización
    filters = extract_filters_with_normalization(query)
    
    # 2. Búsqueda híbrida en ChromaDB
    results = chroma_collection.query(
        query_texts=[query],
        where=filters,
        n_results=10
    )
    
    # 3. Construir prompt con contexto y trazabilidad
    context = format_chunks(results['documents'])
    prompt = build_structured_prompt(context, query)
    
    # 4. Generar respuesta con Gemini
    response = gemini.generate(prompt)
    
    # 5. Añadir información de fuente
    response += f"\n\nFuente: {document_id}, Chunk {chunk_position} de {total_chunks}"
    
    return response
```

## 7. Ventajas del MVP Blindado

### 7.1 Simplicidad:
- ✅ **Un solo flujo de consulta** - Sin enrutamiento complejo
- ✅ **Chunking desde el día 1** - Precisión garantizada
- ✅ **ChromaDB como motor único** - Sin sincronización entre sistemas
- ✅ **Prompt estructurado** - LLM maneja la interpretación con instrucciones claras

### 7.2 Robustez:
- ✅ **Validación de embeddings** - Prueba previa con textos legales
- ✅ **Normalización de filtros** - Tolerancia a variaciones en nombres
- ✅ **Fallback recursivo** - Manejo de chunks grandes
- ✅ **Trazabilidad** - Fuente visible en respuestas

### 7.3 Velocidad:
- ✅ **MVP funcional rápidamente** - Validación rápida
- ✅ **Testing unitario** - Validación automática
- ✅ **Sin dependencias externas** - Despliegue inmediato
- ✅ **Iteración rápida** - Fácil de mejorar

### 7.4 Escalabilidad:
- ✅ **Base sólida** - Fácil migración a arquitectura completa
- ✅ **Chunking optimizable** - Mejoras incrementales
- ✅ **Prompts refinables** - Ajustes específicos

## 8. Aclaraciones y Decisiones Pendientes para el MVP Blindado

### 8.1 Estrategia para la Extracción de Filtros (`extract_filters()`)

**🤔 Cuestionamiento:** ¿Cómo exactamente se traducirá una consulta en lenguaje natural (ej: "embargos de Nury Romero") a un filtro de base de datos (`{"demandante": "Nury Romero", "tipo_medida": "Embargo"}`)?

**✅ Aclaración explícita para el plan:** Para el **MVP**, la función `extract_filters()` se implementará con una estrategia simple basada en **palabras clave y expresiones regulares**. Se crearán patrones para detectar fechas, cuantías y términos jurídicos comunes (ej: "embargo", "demanda"). Para nombres propios, se usará una búsqueda de coincidencia parcial con **normalización** (minúscula, sin tildes). Se reconoce que este método es una simplificación y su mejora será un objetivo para futuras fases.

### 8.2 Manejo de "Chunks" de Gran Tamaño

**🤔 Cuestionamiento:** ¿Qué pasará si un párrafo individual dentro de un documento supera el tamaño máximo definido para un chunk (512 tokens)?

**✅ Aclaración explícita para el plan:** La estrategia de chunking debe incluir un **mecanismo de fallback recursivo**. Si un párrafo excede el `CHUNK_SIZE`, será dividido **recursivamente por oraciones**, hasta que todos los fragmentos resultantes estén por debajo del límite. Esto garantiza que no se pierda información por truncamiento.

### 8.3 Medición de Calidad y Precisión

**🤔 Cuestionamiento:** ¿Cómo se medirá de forma realista el criterio de éxito de "Precisión > 80%" para el MVP?

**✅ Aclaración explícita para el plan:** Se reemplazará la métrica cuantitativa por una **evaluación cualitativa**. Se definirá un set de **20 preguntas de prueba representativas**. Las respuestas del sistema serán evaluadas por un experto en el dominio bajo una escala simple (ej: Correcta, Parcialmente Correcta, Incorrecta). El objetivo del MVP es que la mayoría de las respuestas caigan en las dos primeras categorías.

### 8.4 Selección del Modelo de Embeddings

**🤔 Cuestionamiento:** "Sentence Transformers" es una librería, ¿qué modelo específico se utilizará para generar los embeddings?

**✅ Aclaración explícita para el plan:** Para el MVP se utilizará el modelo `paraphrase-multilingual-mpnet-base-v2` por su balance entre rendimiento y soporte multilingüe, incluyendo el español. **Antes de indexar todo el corpus**, se realizará una **validación previa** con 5 documentos representativos y 10 preguntas de prueba para asegurar que el modelo funciona bien con textos legales colombianos. Si no cumple las expectativas, se evaluarán alternativas como `all-MiniLM-L6-v2` o `distiluse-base-multilingual-cased-v2`.

### 8.5 Trazabilidad de Respuestas

**🤔 Cuestionamiento:** ¿Cómo se garantizará que las respuestas sean trazables a su fuente?

**✅ Aclaración explícita para el plan:** Cada respuesta generada por el sistema incluirá al final la información de fuente en el formato: "Fuente: {document_id}, Chunk {chunk_position} de {total_chunks}". Esto proporciona trazabilidad mínima sin implementar un motor de explicación formal, permitiendo verificar de dónde proviene la información.

## 9. Criterios de Éxito del MVP Blindado

### 9.1 Funcionalidad:
- [ ] Embeddings validados para textos legales
- [ ] Chunking funcional con fallback recursivo
- [ ] Búsqueda híbrida operativa con normalización
- [ ] Respuestas coherentes a preguntas específicas
- [ ] Integración con Gemini funcionando
- [ ] Trazabilidad en respuestas

### 9.2 Rendimiento:
- [ ] Respuestas en menos de 3 segundos
- [ ] Evaluación cualitativa con 20 preguntas de prueba
- [ ] Cobertura > 90% de documentos
- [ ] Testing unitario pasando

### 9.3 Escalabilidad:
- [ ] Capacidad para 1,000+ documentos
- [ ] Fácil migración a arquitectura completa
- [ ] Base para iteraciones futuras

Esta estrategia blindada aborda todos los puntos críticos identificados y proporciona un MVP funcional, robusto y que valida la viabilidad del sistema RAG de extremo a extremo. Las aclaraciones anteriores eliminan las ambigüedades y establecen decisiones claras para el desarrollo, incluyendo validación previa de embeddings, testing unitario y trazabilidad de respuestas.
