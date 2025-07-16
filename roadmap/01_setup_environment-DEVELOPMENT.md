# Guía de Desarrollo - Sistema RAG para Expedientes Jurídicos

## Configuración Inicial

### Prerrequisitos
- Python 3.8 o superior
- pip actualizado
- Acceso a API de Google (Gemini)

### Pasos de Configuración
1. Clonar el repositorio
2. Ejecutar: `python setup.py`
3. Configurar `.env` con tu API key de Google
4. Ejecutar: `python -m pytest tests/` para verificar instalación

## Estructura del Proyecto

### Organización por Capas (Arquitectura Limpia)
```
src/
├── chunking/          # División de documentos en chunks
├── indexing/          # Generación de embeddings e indexación
├── query/             # Procesamiento de consultas y respuestas
├── testing/           # Validación de embeddings y evaluación
├── utils/             # Utilidades compartidas
└── resources/         # Recursos estáticos (metadatos, etc.)

data/
├── raw/               # Datos de entrada sin procesar
├── processed/         # Datos procesados
└── chroma_db/         # Base de datos vectorial

tests/
├── unit/              # Tests unitarios
└── integration/       # Tests de integración

config/                # Configuraciones centralizadas
logs/                  # Logs del sistema
```

### Principios de Diseño Aplicados

#### SOLID Principles
- **SRP**: Cada módulo tiene una responsabilidad única
- **OCP**: Abierto para extensión, cerrado para modificación
- **LSP**: Interfaces sustituibles
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
# Configurar entorno
python setup.py

# Ejecutar tests
python -m pytest

# Tests con cobertura
python -m pytest --cov=src

# Ejecutar linting
python -m flake8 src/

# Validar tipos
python -m mypy src/
```

### Logging
- **Nivel**: INFO por defecto
- **Formato**: Sin emojis, texto estructurado
- **Archivo**: `logs/rag_system.log`

### Testing
- **Unitarios**: Componentes individuales
- **Integración**: Flujos completos
- **Validación**: Embeddings y respuestas

## Configuración

### Variables de Entorno (.env)
```bash
GOOGLE_API_KEY=tu_api_key_aqui
```

### Configuración Centralizada (config/settings.py)
- Configuración de APIs
- Parámetros de chunking
- Configuración de ChromaDB
- Parámetros de testing

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
- Tests de integración para flujos
- Validación de embeddings
- Evaluación cualitativa de respuestas

## Arquitectura del Sistema

### Flujo Principal
1. **Chunking**: División de documentos en chunks optimizados
2. **Indexing**: Generación de embeddings y almacenamiento
3. **Query**: Procesamiento de consultas y generación de respuestas
4. **Testing**: Validación y evaluación continua

### Componentes Clave
- **ChromaDB**: Base de datos vectorial
- **SQLite**: Metadatos canónicos
- **Gemini 2.0 Flash Lite**: LLM para respuestas
- **Sentence Transformers**: Embeddings multilingües

## Monitoreo y Debugging

### Logs
- Configuración automática en `setup.py`
- Rotación de archivos de log
- Niveles configurables

### Métricas
- Tiempo de respuesta
- Precisión de embeddings
- Calidad de respuestas
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