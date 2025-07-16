# Arquitectura de Pipeline de Procesamiento de Documentos

## 🏗️ Principios de Diseño

Este proyecto implementa una arquitectura de pipeline siguiendo los principios **SOLID** y **GRASP**:

### SOLID Principles
- **S** - Single Responsibility Principle (SRP): Cada clase tiene una única responsabilidad
- **O** - Open/Closed Principle (OCP): Abierto para extensión, cerrado para modificación
- **L** - Liskov Substitution Principle (LSP): Las implementaciones son intercambiables
- **I** - Interface Segregation Principle (ISP): Interfaces específicas y cohesivas
- **D** - Dependency Inversion Principle (DIP): Depende de abstracciones, no de implementaciones

### GRASP Patterns
- **High Cohesion**: Responsabilidades relacionadas están agrupadas
- **Low Coupling**: Mínima dependencia entre componentes
- **Information Expert**: Cada clase maneja su propia información
- **Creator**: Clases responsables de crear instancias
- **Controller**: Coordinación centralizada

## 📁 Estructura del Proyecto

```
src/
├── domain/                           # Capa de dominio (interfaces)
│   ├── i_pipeline_step.py           # Interfaz para pasos del pipeline
│   ├── i_document_processor.py      # Interfaz para procesamiento
│   └── i_file_handler.py            # Interfaz para manejo de archivos
├── infrastructure/                   # Capa de infraestructura (implementaciones)
│   ├── pipeline_steps/              # Pasos del pipeline
│   │   ├── ocr_step.py             # Paso de OCR
│   │   └── metadata_extraction_step.py # Paso de metadata
│   ├── pipeline_config.py           # Configuración del pipeline
│   ├── docling_api_processor.py     # Procesador de API
│   └── local_file_handler.py        # Manejador de archivos
├── application/                      # Capa de aplicación (orquestación)
│   └── document_pipeline_orchestrator.py # Orquestador principal
└── main.py                          # Punto de entrada
```

## 🔄 Flujo del Pipeline

### 1. Configuración
```python
# Validación de configuración
api_base_url, config = validate_configuration()

# Creación de componentes
file_handler = LocalFileHandler(source_dir=config.source_directory, target_dir=config.target_directory)
pipeline_steps = create_pipeline_steps(api_base_url, config)
```

### 2. Orquestación
```python
# Orquestador principal
orchestrator = DocumentPipelineOrchestrator(
    file_handler=file_handler,
    pipeline_steps=pipeline_steps,
    max_workers=config.max_workers
)

# Ejecución del pipeline
orchestrator.execute_pipeline(output_formats=config.output_formats)
```

### 3. Ejecución de Pasos
Cada documento pasa por los siguientes pasos en secuencia:

1. **OCR Step**: Extracción de texto mediante Docling API
2. **Metadata Extraction Step**: Extracción de metadata del archivo y contenido
3. **Future Steps**: Pasos adicionales configurables

## 🧩 Componentes Principales

### IPipelineStep (Interfaz)
```python
class IPipelineStep(ABC):
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        pass
    
    @abstractmethod
    def can_execute(self, input_data: Dict[str, Any]) -> bool:
        pass
```

**Principios aplicados:**
- **SRP**: Define solo el contrato para pasos del pipeline
- **ISP**: Interfaz específica y cohesiva
- **DIP**: Dependencia de abstracción, no implementación

### OCRStep (Implementación)
```python
class OCRStep(IPipelineStep):
    def __init__(self, document_processor: DoclingApiProcessor):
        self.document_processor = document_processor  # Inyección de dependencia
```

**Principios aplicados:**
- **SRP**: Solo se encarga del OCR
- **DIP**: Recibe dependencia inyectada
- **LSP**: Implementa correctamente la interfaz

### DocumentPipelineOrchestrator
```python
class DocumentPipelineOrchestrator:
    def __init__(self, file_handler: IFileHandler, pipeline_steps: List[IPipelineStep], max_workers: int):
        # Inyección de dependencias
```

**Principios aplicados:**
- **SRP**: Solo orquesta la ejecución
- **High Cohesion**: Todas las responsabilidades están relacionadas
- **Low Coupling**: Depende de interfaces, no implementaciones

### PipelineConfig
```python
@dataclass
class PipelineConfig:
    # Configuración centralizada
    enable_ocr: bool = True
    enable_metadata_extraction: bool = True
    # ...
```

**Principios aplicados:**
- **SRP**: Solo maneja configuración
- **Information Expert**: Centraliza información de configuración
- **Creator**: Factory method para crear configuraciones

## 🔧 Extensibilidad

### Agregar Nuevos Pasos

1. **Crear nueva implementación**:
```python
class NewStep(IPipelineStep):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Lógica del nuevo paso
        return enriched_data
```

2. **Actualizar configuración**:
```python
@dataclass
class PipelineConfig:
    enable_new_step: bool = False  # Nueva opción
```

3. **Actualizar factory method**:
```python
def create_pipeline_steps(api_base_url: str, config: PipelineConfig) -> list:
    # ...
    if config.enable_new_step:
        pipeline_steps.append(NewStep())
    return pipeline_steps
```

### Configuración por Variables de Entorno

```env
API_BASE_URL=http://localhost:8000
MAX_WORKERS=10
SOURCE_DIR=src/resources/docs
TARGET_DIR=target
OUTPUT_FORMATS=json,html,text
```

## 🎯 Ventajas de la Arquitectura

### ✅ **Mantenibilidad**
- Separación clara de responsabilidades
- Código modular y reutilizable
- Fácil testing de componentes individuales

### ✅ **Extensibilidad**
- Nuevos pasos sin modificar código existente (OCP)
- Configuración flexible
- Plug-and-play de componentes

### ✅ **Testabilidad**
- Inyección de dependencias
- Interfaces bien definidas
- Componentes aislados

### ✅ **Escalabilidad**
- Procesamiento paralelo
- Configuración de workers
- Pipeline configurable

### ✅ **Robustez**
- Validación de entrada en cada paso
- Manejo de errores por paso
- Logging detallado

## 🚀 Uso

### Ejecución Básica
```bash
python -m src.main
```

### Configuración Personalizada
```python
config = PipelineConfig(
    enable_ocr=True,
    enable_metadata_extraction=True,
    enable_legal_reference_extraction=False,
    max_workers=5
)
```

### Monitoreo
El pipeline proporciona logging detallado:
```
🎯 Iniciando pipeline de procesamiento de documentos...
⚙️ Pasos configurados: 2
   1. ocr_extraction: Extracción de texto mediante OCR usando Docling API
   2. metadata_extraction: Extracción de metadata del documento y contenido OCR
📄 Documentos encontrados: 3
⚡ Procesando con hasta 10 workers...
🚀 Iniciando pipeline para: documento1.pdf
📋 Paso 1/2: ocr_extraction
🔍 [OCR] Procesando: documento1.pdf
✅ [OCR] Completado: documento1.pdf
✅ Paso 1 completado: ocr_extraction
📋 Paso 2/2: metadata_extraction
📊 [Metadata] Extrayendo metadata de: documento1.pdf
✅ [Metadata] Completado: documento1.pdf
✅ Paso 2 completado: metadata_extraction
✅ Completado: documento1.pdf
```

## 🔮 Futuras Extensiones

### Pasos Planificados
- **LegalReferenceExtractionStep**: Extracción de referencias legales
- **VectorizationStep**: Vectorización para búsqueda semántica
- **DatabaseStorageStep**: Almacenamiento en base de datos
- **QualityValidationStep**: Validación de calidad del OCR

### Mejoras Arquitectónicas
- **Plugin System**: Carga dinámica de pasos
- **Configuration Management**: Configuración desde archivos YAML/JSON
- **Metrics Collection**: Métricas de rendimiento
- **Error Recovery**: Recuperación automática de errores

---

Esta arquitectura proporciona una base sólida y extensible para el procesamiento de documentos, siguiendo las mejores prácticas de diseño de software. 