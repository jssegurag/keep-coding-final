# Pipeline de Extracción OCR - Proyecto Migrado

## Descripción
Este proyecto contiene el pipeline de extracción OCR migrado desde el proyecto original.

## Estructura del Proyecto
```
keep-coding-final/
├── .env                    # Variables de entorno
├── requirements.txt        # Dependencias de Python
├── README.md              # Este archivo
├── test_imports.py        # Script de verificación de imports
├── test_config.py         # Script de verificación de configuración
├── src/
│   ├── __init__.py
│   ├── main.py            # Punto de entrada principal
│   ├── domain/            # Capa de dominio (interfaces)
│   │   ├── __init__.py
│   │   ├── i_document_processor.py
│   │   └── i_file_handler.py
│   ├── infrastructure/    # Capa de infraestructura (implementaciones)
│   │   ├── __init__.py
│   │   ├── docling_api_processor.py
│   │   ├── local_file_handler.py
│   │   └── utils.py
│   ├── application/       # Capa de aplicación (casos de uso)
│   │   ├── __init__.py
│   │   └── process_documents_use_case.py
│   └── resources/
│       └── docs/          # Documentos fuente
└── target/                # Directorio de salida
```

## Instalación

### 1. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Editar el archivo `.env` con la configuración apropiada:
```env
API_BASE_URL=http://localhost:8000
MAX_WORKERS=10
```

## Uso

### Verificar instalación
```bash
python test_imports.py
python test_config.py
```

### Ejecutar pipeline
```bash
python -m src.main
```

## Arquitectura
Este proyecto sigue la arquitectura limpia (Clean Architecture) con separación de capas:

- **Domain Layer**: Interfaces abstractas
- **Infrastructure Layer**: Implementaciones concretas
- **Application Layer**: Casos de uso
- **Main**: Punto de entrada y configuración

## Migración
Este proyecto fue migrado automáticamente desde: /Users/mb/Documents/PoC/docling-ocr-cloud-run
Fecha de migración: sábado, 12 de julio de 2025, 00:33:34 -05
```
