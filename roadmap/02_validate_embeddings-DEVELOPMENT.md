# Guía de Desarrollo - Validación de Embeddings para Textos Legales

## Configuración Inicial

### Prerrequisitos
- Python 3.8 o superior
- Dependencias del paso 1 instaladas
- Datos de prueba disponibles (CSV y archivos JSON)

### Pasos de Configuración
1. Verificar que el paso 1 esté completado
2. Ejecutar: `python scripts/validate_embeddings.py`
3. Revisar resultados en `logs/embedding_validation_results.json`
4. Ejecutar: `python -m pytest tests/unit/test_embedding_validator.py -v`

## Estructura del Proyecto

### Organización por Capas (Arquitectura Limpia)
```
src/
├── testing/
│   └── embedding_validator.py    # Validador de embeddings
├── utils/
│   └── logger.py                 # Configuración de logging
└── resources/                    # Recursos estáticos

scripts/
└── validate_embeddings.py        # Script de validación

tests/
├── unit/
│   └── test_embedding_validator.py  # Tests unitarios
└── integration/                  # Tests de integración

logs/
└── embedding_validation_results.json  # Resultados de validación

config/
└── settings.py                   # Configuración centralizada
```

### Principios de Diseño Aplicados

#### SOLID Principles
- **SRP**: `EmbeddingValidator` tiene responsabilidad única de validar embeddings
- **OCP**: Abierto para extensión (nuevos tipos de validación)
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
# Ejecutar validación de embeddings
python scripts/validate_embeddings.py

# Ejecutar tests unitarios
python -m pytest tests/unit/test_embedding_validator.py -v

# Tests con cobertura
python -m pytest --cov=src/testing

# Verificar resultados
cat logs/embedding_validation_results.json
```

### Logging
- **Nivel**: INFO por defecto
- **Formato**: Sin emojis, texto estructurado
- **Archivo**: `logs/embedding_validation.log`

### Testing
- **Unitarios**: Componentes individuales del validador
- **Validación**: Embeddings y respuestas
- **Métricas**: Similitud semántica, búsqueda por nombres, conceptos jurídicos

## Configuración

### Variables de Entorno (.env)
```bash
GOOGLE_API_KEY=tu_api_key_aqui
```

### Configuración Centralizada (config/settings.py)
- Modelo de embeddings: `paraphrase-multilingual-mpnet-base-v2`
- Rutas de datos: CSV y JSON
- Parámetros de validación
- Configuración de logging

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
- Validación de embeddings
- Evaluación cualitativa de respuestas
- Mocks para dependencias externas

## Arquitectura del Sistema

### Flujo Principal
1. **Carga de Documentos**: Cargar 5 documentos representativos
2. **Extracción de Texto**: Procesar estructura DoclingDocument
3. **Generación de Chunks**: Dividir texto en chunks optimizados
4. **Validación de Embeddings**: Probar 3 tipos de búsqueda
5. **Cálculo de Métricas**: Evaluar rendimiento del modelo

### Componentes Clave
- **EmbeddingValidator**: Validador principal
- **SentenceTransformer**: Modelo de embeddings
- **Test Documents**: Documentos de prueba
- **Metrics Calculator**: Calculador de métricas

## Monitoreo y Debugging

### Logs
- Configuración automática en `src/utils/logger.py`
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