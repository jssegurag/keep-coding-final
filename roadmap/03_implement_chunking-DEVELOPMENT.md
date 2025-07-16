# Guía de Desarrollo - Sistema de Chunking para Documentos Legales

## Configuración Inicial

### Prerrequisitos
- Python 3.8 o superior
- Dependencias del paso 1 y 2 instaladas
- Datos de entrada disponibles (CSV y archivos JSON de OCR)
- Sistema de embeddings validado del paso 2

### Pasos de Configuración
1. Verificar que los pasos 1 y 2 estén completados
2. Ejecutar: `python scripts/test_chunking_real_docs.py`
3. Revisar resultados en `logs/chunking_effectiveness_report.json`
4. Ejecutar: `python -m pytest tests/unit/test_chunking.py -v`

## Estructura del Proyecto

### Organización por Capas (Arquitectura Limpia)
```
src/
├── chunking/
│   └── document_chunker.py     # Sistema principal de chunking
├── utils/
│   └── text_utils.py           # Utilidades de procesamiento de texto
└── resources/                  # Recursos estáticos

scripts/
└── test_chunking_real_docs.py  # Script de análisis de efectividad

tests/
├── unit/
│   └── test_chunking.py        # Tests unitarios del chunking
└── integration/                 # Tests de integración

logs/
└── chunking_effectiveness_report.json  # Reporte de efectividad

config/
└── settings.py                  # Configuración centralizada
```

### Principios de Diseño Aplicados

#### SOLID Principles
- **SRP**: `DocumentChunker` tiene responsabilidad única de chunking
- **OCP**: Abierto para extensión (nuevas estrategias de chunking)
- **LSP**: Interfaces sustituibles (`IChunkingStrategy`)
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
# Ejecutar análisis de efectividad con documentos reales
python scripts/test_chunking_real_docs.py

# Ejecutar tests unitarios
python -m pytest tests/unit/test_chunking.py -v

# Tests con cobertura
python -m pytest --cov=src/chunking

# Verificar resultados
cat logs/chunking_effectiveness_report.json

# Probar chunking básico
python scripts/test_chunking.py
```

### Logging
- **Nivel**: INFO por defecto
- **Formato**: Sin emojis, texto estructurado
- **Archivo**: `logs/chunking.log`

### Testing
- **Unitarios**: Componentes individuales del chunker
- **Validación**: Chunks y metadatos
- **Métricas**: Tamaño de chunks, overlap, preservación de contexto

## Configuración

### Variables de Entorno (.env)
```bash
# No se requieren variables específicas para chunking
# Las configuraciones están en config/settings.py
```

### Configuración Centralizada (config/settings.py)
- `CHUNK_SIZE`: Tamaño máximo de chunk en tokens (512)
- `CHUNK_OVERLAP`: Overlap entre chunks consecutivos (50)
- `MAX_CHUNK_SIZE`: Tamaño máximo permitido (1024)
- `MIN_CHUNK_SIZE`: Tamaño mínimo permitido (50)
- Rutas de datos: CSV y JSON de OCR

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
- Validación de chunks
- Evaluación de calidad de chunking
- Mocks para dependencias externas

## Arquitectura del Sistema

### Flujo Principal
1. **Carga de Documentos**: Cargar documentos JSON de OCR
2. **Extracción de Texto**: Procesar estructura DoclingDocument
3. **Limpieza de Texto**: Normalizar y limpiar texto
4. **Chunking Adaptativo**: Dividir con fallback recursivo
5. **Validación de Chunks**: Verificar calidad y metadatos
6. **Análisis de Efectividad**: Calcular métricas de calidad

### Componentes Clave
- **DocumentChunker**: Chunker principal con fallback recursivo
- **Tokenizer**: Tokenización y conteo de tokens
- **ChunkValidator**: Validación de calidad de chunks
- **TextNormalizer**: Normalización y limpieza de texto
- **LegalEntityExtractor**: Extracción de entidades legales

## Monitoreo y Debugging

### Logs
- Configuración automática en `src/utils/logger.py`
- Rotación de archivos de log
- Niveles configurables

### Métricas
- Tasa de éxito de chunking
- Distribución de tamaños de chunks
- Preservación de contexto
- Extracción de entidades legales

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

### Sistema de Chunking
- **Fallback Recursivo**: División inteligente por párrafos → oraciones → palabras
- **Overlap Configurable**: Preservación de contexto entre chunks
- **Validación Automática**: Verificación de calidad y metadatos
- **Preservación de Metadatos**: Contexto jurídico mantenido

### Utilidades de Texto
- **Normalización**: Limpieza y estandarización de texto
- **Extracción de Entidades**: Nombres, fechas, cantidades, términos legales
- **Análisis de Complejidad**: Métricas de legibilidad y estructura
- **Detección de Idioma**: Identificación automática de idioma

### Estrategias de Chunking
- **ParagraphChunkingStrategy**: División por párrafos
- **SentenceChunkingStrategy**: División por oraciones
- **Interfaz Extensible**: Nuevas estrategias fácilmente añadibles

## Métricas de Calidad

### Efectividad del Chunking
- **Tasa de Éxito**: > 95% de chunks dentro del tamaño configurado
- **Distribución Óptima**: Mayoría de chunks en rango 50-200 tokens
- **Overlap Efectivo**: Preservación de contexto entre chunks
- **Metadatos Completos**: Información jurídica preservada

### Extracción de Entidades
- **Nombres**: Identificación de personas y entidades
- **Fechas**: Detección de fechas en múltiples formatos
- **Cantidades**: Extracción de montos monetarios
- **Términos Legales**: Identificación de conceptos jurídicos
- **Números de Documento**: Detección de referencias legales

## Integración con Otros Pasos

### Con Paso 2 (Validación de Embeddings)
- Chunks compatibles con modelo `paraphrase-multilingual-mpnet-base-v2`
- Preservación de contexto semántico
- Metadatos para filtrado híbrido

### Con Paso 4 (Indexación)
- Preparación directa para ChromaDB
- Metadatos normalizados para búsqueda
- Embeddings optimizados para chunks

## Troubleshooting

### Problemas Comunes
1. **Chunks muy grandes**: Ajustar `CHUNK_SIZE` en configuración
2. **Pérdida de contexto**: Verificar `CHUNK_OVERLAP`
3. **Metadatos incompletos**: Revisar extracción de entidades
4. **Rendimiento lento**: Optimizar estrategias de chunking

### Soluciones
- **Configuración adaptativa**: Ajustar parámetros según tipo de documento
- **Validación continua**: Monitoreo de calidad de chunks
- **Logging detallado**: Seguimiento de proceso de chunking
- **Tests exhaustivos**: Verificación de casos edge

## Estado del Desarrollo

### Completado ✅
- Sistema de chunking con fallback recursivo
- Validación automática de chunks
- Extracción de entidades legales
- Tests unitarios completos
- Análisis de efectividad con documentos reales

### En Desarrollo 🔄
- Optimización de parámetros para documentos complejos
- Mejoras en estrategias de chunking
- Integración con sistema de indexación

### Pendiente 📋
- Chunking adaptativo basado en complejidad
- Análisis de secciones legales específicas
- Optimización para documentos muy largos 