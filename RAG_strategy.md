# Estrategia RAG para Documentos Jurídicos con DoclingDocument JSON

## 📋 Índice

1. [Análisis del Contexto](#análisis-del-contexto)
2. [Estrategia de Procesamiento](#estrategia-de-procesamiento)
3. [Arquitectura de Base de Datos Vectorial](#arquitectura-de-base-de-datos-vectorial)
4. [Estrategias de Vectorización](#estrategias-de-vectorización)
5. [Estrategias de Retrieval](#estrategias-de-retrieval)
6. [Implementación Práctica](#implementación-práctica)
7. [Casos de Uso Específicos](#casos-de-uso-específicos)
8. [Consideraciones de Rendimiento](#consideraciones-de-rendimiento)

## 🎯 Análisis del Contexto

### Características Específicas de Documentos Jurídicos

Los documentos jurídicos presentan características únicas que requieren un procesamiento especializado:

#### **Estructura Jerárquica Compleja:**
- **Encabezados**: Títulos, subtítulos, secciones, artículos
- **Referencias Cruzadas**: Citas legales, números de expediente
- **Metadata Jurídica**: Fechas, jurisdicciones, autoridades
- **Elementos Visuales**: Firmas, sellos, logos institucionales

#### **Tablas Variables:**
- **Tamaños Dinámicos**: Desde tablas pequeñas hasta complejas
- **Información Crítica**: Fechas, montos, referencias legales
- **Relaciones Estructurales**: Headers, celdas combinadas, spans

#### **Información Contextual:**
- **Referencias Legales**: Artículos, leyes, decretos
- **Procedimientos**: Números de radicación, expedientes
- **Temporalidad**: Fechas de presentación, vencimientos

### Análisis del JSON de DoclingDocument

Basándonos en el análisis de la estructura JSON, identificamos:

#### **Elementos Disponibles:**
- **Texts**: 20-66 elementos por documento con labels específicos
- **Tables**: 0-4 elementos con estructura compleja de grid
- **Pictures**: 3-10 elementos con OCR integrado
- **Groups**: 0-5 elementos (key_value_area, form_area, list)

#### **Información de Coordenadas:**
- **Sistema**: BOTTOMLEFT con coordenadas precisas
- **Provenance**: Información de página y bounding boxes
- **Relaciones**: Referencias JSON entre elementos

## 🏗️ Estrategia de Procesamiento

### Fase 1: Extracción Estructurada

#### **A. Procesamiento por Tipo de Elemento**

```python
class LegalDocumentProcessor:
    def process_docling_json(self, json_data):
        chunks = []
        
        # 1. Procesar textos con contexto jurídico
        text_chunks = self.process_legal_texts(json_data['texts'])
        chunks.extend(text_chunks)
        
        # 2. Procesar tablas preservando estructura
        table_chunks = self.process_legal_tables(json_data['tables'])
        chunks.extend(table_chunks)
        
        # 3. Procesar imágenes con OCR
        image_chunks = self.process_legal_images(json_data['pictures'])
        chunks.extend(image_chunks)
        
        # 4. Procesar grupos estructurados
        group_chunks = self.process_legal_groups(json_data['groups'])
        chunks.extend(group_chunks)
        
        return chunks
```

#### **B. Chunking Inteligente**

```python
class IntelligentLegalChunker:
    def chunk_by_type(self, element):
        if element['type'] == 'header':
            return self.create_header_chunk(element)
        elif element['type'] == 'table':
            return self.create_table_chunk(element)
        elif element['type'] == 'text':
            return self.sentence_based_chunking(element)
        elif element['type'] == 'image':
            return self.create_image_chunk(element)
```

### Fase 2: Enriquecimiento Contextual

#### **A. Metadata Jurídica Específica**

```python
def extract_legal_metadata(text):
    metadata = {
        'document_type': 'legal_document',
        'jurisdiction': 'colombia',
        'expedient_number': extract_expedient_number(text),
        'date': extract_date(text),
        'authority': extract_authority(text),
        'legal_references': extract_legal_citations(text),
        'confidence_score': calculate_ocr_confidence(text)
    }
    return metadata
```

#### **B. Contexto Jerárquico**

```python
def build_context_hierarchy(chunk):
    hierarchy = []
    
    # Agregar contexto de página
    hierarchy.append(f"página_{chunk.page_no}")
    
    # Agregar contexto de sección
    if chunk.parent_section:
        hierarchy.append(chunk.parent_section)
    
    # Agregar contexto de artículo
    if chunk.parent_article:
        hierarchy.append(chunk.parent_article)
    
    return hierarchy
```

## 🗄️ Arquitectura de Base de Datos Vectorial

### Estructura del Documento Vectorial

```python
vector_document = {
    # Contenido principal
    "content": "texto del chunk...",
    "content_vector": [0.1, 0.2, 0.3, ...],
    
    # Metadata jurídica
    "legal_metadata": {
        "document_type": "oficio_juridico",
        "expedient_number": "IQ051008152850",
        "jurisdiction": "colombia",
        "date": "2024-01-15",
        "authority": "tribunal_superior",
        "legal_references": ["artículo 123", "ley 1234"],
        "confidence_score": 0.95
    },
    
    # Información estructural
    "structural_metadata": {
        "chunk_type": "text|table|header|image",
        "page_number": 1,
        "bbox": {"l": 100, "t": 200, "r": 300, "b": 250},
        "context_hierarchy": ["título", "sección", "artículo"],
        "parent_chunk_id": "chunk_123"
    },
    
    # Información de búsqueda
    "search_metadata": {
        "keywords": ["expediente", "radicación", "fecha"],
        "semantic_tags": ["procedimiento", "administrativo"],
        "cross_references": ["chunk_456", "chunk_789"]
    }
}
```

### Estrategias de Indexación

#### **A. Índices Múltiples**

```python
# 1. Índice semántico principal
semantic_index = create_vector_index(
    vectors=content_vectors,
    similarity_metric='cosine'
)

# 2. Índice de metadata
metadata_index = create_vector_index(
    vectors=metadata_vectors,
    similarity_metric='cosine'
)

# 3. Índice híbrido
hybrid_index = create_hybrid_index(
    vector_queries=content_vectors,
    keyword_queries=legal_keywords,
    weight_vector=0.7,
    weight_keyword=0.3
)
```

#### **B. Particionamiento por Tipo**

```python
# Separar chunks por tipo para búsquedas especializadas
indexes = {
    'text_chunks': create_index(text_chunks),
    'table_chunks': create_index(table_chunks),
    'header_chunks': create_index(header_chunks),
    'image_chunks': create_index(image_chunks)
}
```

## 🔄 Estrategias de Vectorización

### Vectorización Múltiple

```python
def create_legal_vectors(chunk):
    vectors = {}
    
    # 1. Vector del contenido principal
    vectors['content_vector'] = embed_text(chunk.content)
    
    # 2. Vector de metadata jurídica
    legal_text = f"{chunk.metadata['document_type']} {chunk.metadata['jurisdiction']} {chunk.metadata['expedient_number']}"
    vectors['metadata_vector'] = embed_text(legal_text)
    
    # 3. Vector de contexto estructural
    context_text = " ".join(chunk.context_hierarchy)
    vectors['context_vector'] = embed_text(context_text)
    
    # 4. Vector combinado (para búsqueda híbrida)
    combined_text = f"{chunk.content} {legal_text} {context_text}"
    vectors['combined_vector'] = embed_text(combined_text)
    
    return vectors
```

### Modelos de Embedding Especializados

```python
# Para documentos jurídicos, usar modelos especializados
legal_embedding_models = {
    'content': 'sentence-transformers/all-MiniLM-L6-v2',
    'legal': 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    'spanish_legal': 'dccuchile/bert-base-spanish-wwm-cased'
}
```

## 🔍 Estrategias de Retrieval

### Búsqueda Híbrida

```python
def legal_document_search(query, filters=None):
    results = []
    
    # 1. Búsqueda semántica
    semantic_results = semantic_index.search(
        query_vector=embed_query(query),
        top_k=10
    )
    
    # 2. Búsqueda por metadata
    metadata_results = metadata_index.search(
        query_vector=embed_query(query),
        filters=filters,  # Expediente, fecha, jurisdicción
        top_k=5
    )
    
    # 3. Búsqueda por keywords
    keyword_results = keyword_index.search(
        query=extract_legal_keywords(query),
        top_k=5
    )
    
    # 4. Combinar y re-rank
    combined_results = combine_and_rerank(
        semantic_results, metadata_results, keyword_results
    )
    
    return combined_results
```

### Búsqueda Contextual

```python
def contextual_legal_search(query, context_chunk_id=None):
    # Si tenemos contexto previo, buscar chunks relacionados
    if context_chunk_id:
        related_chunks = find_related_chunks(context_chunk_id)
        context_query = f"{query} {related_chunks}"
    else:
        context_query = query
    
    return semantic_index.search(context_query)
```

## 🛠️ Implementación Práctica

### Con Pinecone

```python
import pinecone

# Configurar Pinecone
pinecone.init(api_key="your_key", environment="your_env")
index_name = "legal-documents"

# Crear índice
pinecone.create_index(
    name=index_name,
    dimension=384,  # Dimensión del embedding
    metric="cosine"
)

# Insertar chunks
index = pinecone.Index(index_name)
index.upsert(vectors=legal_chunks_with_vectors)
```

### Con ChromaDB

```python
import chromadb

# Crear cliente
client = chromadb.Client()

# Crear colección
collection = client.create_collection(
    name="legal_documents",
    metadata={"hnsw:space": "cosine"}
)

# Insertar documentos
collection.add(
    documents=[chunk.content for chunk in chunks],
    metadatas=[chunk.metadata for chunk in chunks],
    embeddings=[chunk.vector for chunk in chunks],
    ids=[chunk.id for chunk in chunks]
)
```

## 📊 Casos de Uso Específicos

### Búsqueda por Expediente

```python
# Buscar todos los chunks de un expediente específico
results = vector_db.search(
    query="expediente IQ051008152850",
    filter={"expedient_number": "IQ051008152850"}
)
```

### Búsqueda por Referencia Legal

```python
# Buscar chunks que mencionen una ley específica
results = vector_db.search(
    query="artículo 123 código civil",
    filter={"legal_references": {"$contains": "artículo 123"}}
)
```

### Búsqueda por Fecha

```python
# Buscar documentos de un período específico
results = vector_db.search(
    query="procedimiento administrativo",
    filter={"date": {"$gte": "2024-01-01", "$lte": "2024-12-31"}}
)
```

### Búsqueda por Tipo de Documento

```python
# Buscar solo tablas o headers
results = vector_db.search(
    query="información de radicación",
    filter={"chunk_type": "table"}
)
```

## ⚡ Consideraciones de Rendimiento

### Optimización de Chunks

#### **A. Tamaño Óptimo de Chunks:**
- **Textos**: 500-1000 tokens
- **Tablas**: Chunk único por tabla
- **Headers**: Chunks separados
- **Imágenes**: Chunk único con OCR

#### **B. Estrategias de Caching:**
```python
# Cache de embeddings
embedding_cache = {}

def get_cached_embedding(text, model_name):
    cache_key = f"{hash(text)}_{model_name}"
    if cache_key not in embedding_cache:
        embedding_cache[cache_key] = embed_text(text, model_name)
    return embedding_cache[cache_key]
```

#### **C. Procesamiento por Lotes:**
```python
def batch_process_chunks(chunks, batch_size=100):
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vectors = embed_batch(batch)
        insert_batch_to_vector_db(batch, vectors)
```

### Monitoreo y Métricas

#### **A. Métricas de Calidad:**
- **Precisión de Retrieval**: % de chunks relevantes recuperados
- **Cobertura**: % de información jurídica capturada
- **Latencia**: Tiempo de respuesta de búsqueda

#### **B. Métricas de Rendimiento:**
- **Throughput**: Chunks procesados por segundo
- **Uso de Memoria**: Consumo de recursos
- **Tiempo de Indexación**: Velocidad de inserción

## 🎯 Ventajas de esta Estrategia

### ✅ Preservación de Estructura Jurídica
- Encabezados como chunks separados
- Tablas con estructura preservada
- Jerarquía de contexto mantenida

### ✅ Metadata Enriquecida
- Información jurídica específica
- Referencias cruzadas
- Confianza del OCR

### ✅ Optimización para Búsqueda
- Chunks semánticamente coherentes
- Contexto preservado
- Relaciones entre elementos

### ✅ Escalabilidad
- Procesamiento por lotes
- Metadata consistente
- Fácil integración con sistemas RAG

## 📈 Implementación en Fases

### Fase 1: Procesamiento Básico
- [ ] Implementar procesador de JSON DoclingDocument
- [ ] Crear chunking básico por tipo de elemento
- [ ] Extraer metadata jurídica básica

### Fase 2: Enriquecimiento Avanzado
- [ ] Implementar extracción de referencias legales
- [ ] Crear sistema de contexto jerárquico
- [ ] Desarrollar vectorización múltiple

### Fase 3: Base de Datos Vectorial
- [ ] Configurar índices múltiples
- [ ] Implementar búsqueda híbrida
- [ ] Optimizar rendimiento

### Fase 4: Integración RAG
- [ ] Conectar con sistema de generación
- [ ] Implementar re-ranking
- [ ] Monitoreo y métricas

---

**Nota**: Esta estrategia está diseñada específicamente para documentos jurídicos colombianos procesados con DoclingDocument JSON, optimizando tanto la precisión como el rendimiento para casos de uso legales específicos.
