# Guía de Desarrollo - Sistema de Indexación para Documentos Legales

## Configuración Inicial

### Prerrequisitos
- Python 3.8 o superior
- Dependencias del paso 1, 2 y 3 instaladas
- Datos de entrada disponibles (CSV actualizado y archivos JSON de OCR)
- Sistema de embeddings validado del paso 2
- Sistema de chunking implementado del paso 3

### Pasos de Configuración
1. Verificar que los pasos 1, 2 y 3 estén completados
2. Ejecutar: `python scripts/update_csv_for_pipeline.py`
3. Ejecutar: `python -m src.main` para procesar pipeline completo
4. Verificar indexación: `python scripts/verify_indexing.py`
5. Ejecutar: `python -m pytest tests/unit/test_indexing.py -v`

## Estructura del Proyecto

### Organización por Capas (Arquitectura Limpia)
```
src/
├── indexing/
│   └── chroma_indexer.py        # Sistema principal de indexación
├── infrastructure/
│   └── pipeline_steps/
│       └── indexing_step.py     # Paso de indexación del pipeline
├── utils/
│   └── logger.py                 # Configuración de logging
└── resources/                    # Recursos estáticos

scripts/
├── update_csv_for_pipeline.py    # Script para actualizar CSV
└── verify_indexing.py           # Script de verificación de indexación

tests/
├── unit/
│   └── test_indexing.py         # Tests unitarios del indexador
└── integration/                  # Tests de integración

logs/
└── indexing_results.json         # Resultados de indexación

config/
└── settings.py                   # Configuración centralizada

data/
└── chroma_db/                   # Base de datos vectorial
```

### Principios de Diseño Aplicados

#### SOLID Principles
- **SRP**: `ChromaIndexer` tiene responsabilidad única de indexación
- **OCP**: Abierto para extensión (nuevos tipos de indexación)
- **LSP**: Interfaces sustituibles (`IPipelineStep`)
- **ISP**: Interfaces específicas por dominio
- **DIP**: Dependencia de abstracciones

#### GRASP Patterns
- **High Cohesion**: Módulos con responsabilidades relacionadas
- **Low Coupling**: Mínima dependencia entre módulos
- **Protected Variations**: Interfaces estables
- **Information Expert**: Responsabilidades asignadas a expertos

## Comandos Útiles

### Desarrollo
```bash
# Actualizar CSV para pipeline
python scripts/update_csv_for_pipeline.py

# Ejecutar pipeline completo con indexación
python -m src.main

# Verificar indexación
python scripts/verify_indexing.py

# Ejecutar tests unitarios
python -m pytest tests/unit/test_indexing.py -v

# Tests con cobertura
python -m pytest --cov=src/indexing

# Verificar resultados
cat logs/indexing_results.json
```

### Logging
- **Nivel**: INFO por defecto
- **Formato**: Sin emojis, texto estructurado
- **Archivo**: `logs/indexing.log`

### Testing
- **Unitarios**: Componentes individuales del indexador
- **Validación**: Embeddings y metadatos
- **Métricas**: Tasa de éxito, calidad de indexación

## Configuración

### Variables de Entorno (.env)
```bash
GOOGLE_API_KEY=tu_api_key_aqui
```

### Configuración Centralizada (config/settings.py)
- `CHROMA_PERSIST_DIRECTORY`: Directorio de ChromaDB
- `CHROMA_COLLECTION_NAME`: Nombre de colección
- `EMBEDDING_MODEL`: Modelo de embeddings
- `EMBEDDING_DIMENSIONS`: Dimensiones de embeddings (768)
- `CSV_METADATA_PATH`: Ruta del CSV actualizado
- `JSON_DOCS_PATH`: Ruta de documentos JSON

## Estándares de Código

### Python
- PEP 8 para estilo
- Type hints obligatorios
- Docstrings descriptivos
- Manejo específico de excepciones

### Logging
- Sin emojis en logs
- Niveles apropiados (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Contexto relevante en mensajes

### Testing
- Tests unitarios para cada componente
- Validación de indexación
- Evaluación de calidad de embeddings
- Mocks para dependencias externas

## Arquitectura del Sistema

### Flujo Principal
1. **Carga de Metadatos**: Cargar CSV actualizado con rutas correctas
2. **Procesamiento de Documentos**: Cargar archivos JSON de OCR
3. **Extracción de Texto**: Concatenar textos de arrays `texts`
4. **Chunking**: Dividir texto en chunks optimizados
5. **Generación de Embeddings**: Crear embeddings con SentenceTransformer
6. **Indexación en ChromaDB**: Almacenar con metadatos normalizados
7. **Validación**: Verificar calidad de indexación

### Componentes Clave
- **ChromaIndexer**: Indexador principal con ChromaDB
- **IndexingStep**: Paso del pipeline de indexación
- **MetadataNormalizer**: Normalización de metadatos
- **EmbeddingGenerator**: Generación de embeddings
- **ChunkProcessor**: Procesamiento de chunks para indexación

## Monitoreo y Debugging

### Logs
- Configuración automática en `src/utils/logger.py`
- Rotación de archivos de log
- Niveles configurables

### Métricas
- Tasa de éxito de indexación
- Calidad de embeddings
- Tiempo de procesamiento
- Uso de recursos

## Contribución

### Flujo de Trabajo
1. Crear rama feature
2. Implementar siguiendo principios SOLID
3. Añadir tests unitarios
4. Ejecutar validaciones
5. Crear pull request

### Criterios de Aceptación
- Tests pasando
- Cobertura > 80%
- Sin code smells
- Documentación actualizada
- Logs sin emojis

## Funcionalidades Implementadas

### Sistema de Indexación
- **Indexación por Documento**: Procesamiento individual con metadatos
- **Indexación por Batch**: Procesamiento en lotes para eficiencia
- **Carga desde CSV**: Integración con metadatos existentes
- **Normalización de Metadatos**: Limpieza y estandarización
- **Verificación de Duplicados**: Prevención de re-indexación

### Integración con Pipeline
- **IndexingStep**: Paso integrado en pipeline principal
- **Configuración Automática**: Habilitación/deshabilitación por configuración
- **Cache Inteligente**: Evita reprocesamiento innecesario
- **Manejo de Errores**: Recuperación robusta de fallos

### Metadatos Jurídicos
- **Información del Demandante**: Nombres, identificación, ubicación
- **Resoluciones**: Números de referencia y radicados
- **Tipo de Entidad**: Clasificación de entidades jurídicas
- **Metadatos de Archivo**: Información técnica del documento

## Métricas de Calidad

### Efectividad de la Indexación
- **Tasa de Éxito**: 100% de documentos procesados exitosamente
- **Cobertura**: 125/130 documentos (96.2% cobertura)
- **Calidad de Embeddings**: Compatible con modelo multilingüe
- **Metadatos Completos**: Información jurídica preservada

### Rendimiento del Sistema
- **Procesamiento Paralelo**: Hasta 30 workers simultáneos
- **Cache Efectivo**: 125 documentos ya procesados
- **Tiempo de Respuesta**: Optimizado para documentos grandes
- **Uso de Memoria**: Eficiente para datasets grandes

## Integración con Otros Pasos

### Con Paso 2 (Validación de Embeddings)
- Modelo `paraphrase-multilingual-mpnet-base-v2` validado
- Dimensiones de embeddings (768) compatibles
- Calidad de embeddings verificada

### Con Paso 3 (Chunking)
- Chunks optimizados para indexación
- Metadatos preservados en chunks
- Overlap configurado para contexto

### Con Pipeline Principal
- Integración automática en `main.py`
- Configuración centralizada en `PipelineConfig`
- Orquestación por `DocumentPipelineOrchestrator`

## Troubleshooting

### Problemas Comunes
1. **Error de columnas CSV**: Verificar estructura del CSV actualizado
2. **Archivos JSON no encontrados**: Verificar rutas en configuración
3. **Embeddings duplicados**: Verificar IDs únicos en ChromaDB
4. **Metadatos incompletos**: Revisar normalización de datos

### Soluciones
- **Script de Actualización**: `update_csv_for_pipeline.py` para corregir rutas
- **Validación de Rutas**: Verificación automática de archivos
- **Normalización Robusta**: Manejo de valores None y datos incompletos
- **Logging Detallado**: Seguimiento completo del proceso

## Estado del Desarrollo

### Completado ✅
- Sistema de indexación con ChromaDB
- Integración completa con pipeline principal
- Normalización robusta de metadatos
- Tests unitarios completos
- Scripts de verificación y actualización
- 125 documentos indexados exitosamente

### Resultados Obtenidos
- **Documentos Procesados**: 125/130 (96.2% cobertura)
- **Tasa de Éxito**: 100% en indexación
- **Chunks Generados**: Variable según complejidad del documento
- **Tiempo de Procesamiento**: Optimizado con cache
- **Calidad de Embeddings**: Compatible con modelo multilingüe

### En Desarrollo 🔄
- Optimización de parámetros para documentos complejos
- Mejoras en estrategias de indexación
- Integración con sistema de consultas

### Pendiente 📋
- Sistema de consultas semánticas
- Evaluación cualitativa de respuestas
- Optimización para consultas complejas
- Integración con interfaz de usuario

## Configuración de Producción

### Variables Críticas
```python
# config/settings.py
CHROMA_PERSIST_DIRECTORY = "data/chroma_db"
CHROMA_COLLECTION_NAME = "legal_documents"
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIMENSIONS = 768
CSV_METADATA_PATH = "src/resources/metadata/pipeline_metadata.csv"
```

### Monitoreo
- Logs de indexación en `logs/indexing.log`
- Métricas de rendimiento
- Verificación de integridad de datos
- Alertas de errores críticos

## Próximos Pasos

### Paso 5: Sistema de Consultas
- Implementación de búsqueda semántica
- Procesamiento de consultas naturales
- Generación de respuestas con LLM
- Evaluación de calidad de respuestas

### Integración Completa
- Pipeline end-to-end funcional
- Sistema RAG completo para expedientes jurídicos
- Interfaz de usuario para consultas
- Monitoreo y métricas de producción 