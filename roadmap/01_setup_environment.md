# 01. Configuración del Entorno de Desarrollo - MVP RAG

## 🎯 Objetivo
Configurar el entorno de desarrollo completo para el sistema RAG de expedientes jurídicos, incluyendo todas las dependencias, estructura de carpetas y configuración inicial.

## 📋 Tareas a Ejecutar

### 1. Crear Estructura de Carpetas
```bash
# Crear estructura principal
mkdir -p src/{chunking,indexing,query,testing,utils}
mkdir -p src/resources/metadata
mkdir -p data/{raw,processed,chroma_db}
mkdir -p tests/{unit,integration}
mkdir -p config
mkdir -p logs
```

### 2. Crear Archivo de Dependencias
Crear `requirements.txt` con las siguientes dependencias:
```
chromadb==0.4.22
google-generativeai==0.8.3
sentence-transformers==2.5.1
pandas==2.1.4
numpy==1.24.3
python-dotenv==1.0.0
pytest==7.4.3
pytest-cov==4.1.0
```

### 3. Crear Archivo de Configuración
Crear `config/settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL = "gemini-2.0-flash-lite"  # Modelo económico para MVP

# Configuración de embeddings
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_DIMENSIONS = 512

# Configuración de chunking
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Configuración de ChromaDB
CHROMA_PERSIST_DIRECTORY = "data/chroma_db"
CHROMA_COLLECTION_NAME = "legal_documents"

# Configuración de SQLite para metadatos canónicos
SQLITE_DB_PATH = "data/legal_docs.db"

# Configuración de archivos
CSV_METADATA_PATH = "src/resources/metadata/studio_results_20250715_2237.csv"
TARGET_PATH = "target/"
JSON_DOCS_PATH = "target/"

# Configuración de testing
TEST_DOCS_COUNT = 5  # Documentos para validación de embeddings
TEST_QUESTIONS_COUNT = 10  # Preguntas para validación inicial
VALIDATION_QUESTIONS_COUNT = 20  # Preguntas para evaluación cualitativa
```

### 4. Crear Archivo .env
Crear `.env` (no incluir en git):
```
GOOGLE_API_KEY=tu_api_key_aqui
```

### 5. Crear Archivo .gitignore
Crear `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Data
data/chroma_db/
data/processed/
*.db
*.sqlite

# Logs
logs/
*.log

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### 6. Crear Archivos __init__.py
Crear archivos `__init__.py` en todas las carpetas de módulos:
```python
# src/__init__.py
# src/chunking/__init__.py
# src/indexing/__init__.py
# src/query/__init__.py
# src/testing/__init__.py
# src/utils/__init__.py
# tests/__init__.py
# tests/unit/__init__.py
# tests/integration/__init__.py
```

### 7. Crear Script de Instalación
Crear `setup.py`:
```python
#!/usr/bin/env python3
"""
Script de configuración inicial del proyecto RAG
"""
import subprocess
import sys
import os

def install_requirements():
    """Instalar dependencias del proyecto"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar dependencias")
        sys.exit(1)

def create_directories():
    """Crear estructura de directorios"""
    directories = [
        "src/chunking", "src/indexing", "src/query", "src/testing", "src/utils",
        "src/resources/metadata",
        "data/raw", "data/processed", "data/chroma_db",
        "tests/unit", "tests/integration",
        "config", "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Creado directorio: {directory}")

def main():
    print("🚀 Configurando entorno de desarrollo RAG...")
    create_directories()
    install_requirements()
    print("✅ Entorno configurado correctamente")

if __name__ == "__main__":
    main()
```

### 8. Crear README de Desarrollo
Crear `DEVELOPMENT.md`:
```markdown
# Guía de Desarrollo - Sistema RAG

## Configuración Inicial
1. Clonar el repositorio
2. Ejecutar: `python setup.py`
3. Configurar `.env` con tu API key de Google
4. Ejecutar: `python -m pytest tests/` para verificar instalación

## Estructura del Proyecto
- `src/`: Código fuente organizado por módulos
- `data/`: Datos de entrada, procesados y base vectorial
- `tests/`: Tests unitarios e integración
- `config/`: Configuraciones del sistema
- `logs/`: Logs de ejecución

## Comandos Útiles
- `python setup.py`: Configurar entorno
- `python -m pytest`: Ejecutar tests
- `python -m pytest --cov=src`: Tests con cobertura
```

## ✅ Criterios de Éxito
- [ ] Todas las carpetas creadas correctamente
- [ ] `requirements.txt` creado con dependencias correctas
- [ ] `config/settings.py` configurado y funcional
- [ ] `.env` creado (sin commitear)
- [ ] `.gitignore` configurado apropiadamente
- [ ] `setup.py` ejecutado sin errores
- [ ] Tests básicos pasando

## 🔍 Verificación
Ejecutar los siguientes comandos para verificar la configuración:
```bash
python setup.py
python -c "from config.settings import *; print('✅ Configuración cargada correctamente')"
python -m pytest tests/ -v
```

## 📝 Notas Importantes
- Asegúrate de tener Python 3.8+ instalado
- La API key de Google debe ser válida
- Todos los archivos deben seguir las convenciones de Python
- La estructura debe ser consistente con el roadmap general 