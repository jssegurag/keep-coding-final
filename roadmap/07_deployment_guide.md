# 07. Guía de Despliegue y Documentación Final - MVP RAG

## 🎯 Objetivo
Crear la documentación completa para el despliegue del MVP RAG, incluyendo guías de usuario, configuración de producción y mantenimiento.

## 📋 Tareas a Ejecutar

### 1. Crear README Principal
Crear `README.md`:
```markdown
# Sistema RAG para Expedientes Jurídicos - MVP

## 🎯 Descripción
Sistema de Retrieval-Augmented Generation (RAG) para consulta inteligente de expedientes jurídicos colombianos. Permite búsquedas por metadatos, preguntas específicas sobre contenido y resúmenes completos mediante una interfaz de chat.

## 🚀 Características Principales

### ✅ Funcionalidades Implementadas
- **Chunking Inteligente**: División de documentos con fallback recursivo
- **Indexación Vectorial**: ChromaDB con embeddings multilingües
- **Búsqueda Híbrida**: Combinación de filtros y similitud semántica
- **Generación con Gemini**: Respuestas contextuales con trazabilidad
- **Normalización Robusta**: Tolerancia a variaciones en nombres y fechas
- **Testing Completo**: Validación de embeddings y evaluación cualitativa

### 🔧 Stack Tecnológico
- **Base Vectorial**: ChromaDB con SQLite
- **Embeddings**: `paraphrase-multilingual-mpnet-base-v2`
- **LLM**: Google Gemini 2.0 Flash Lite
- **Procesamiento**: Python 3.8+
- **Testing**: pytest con cobertura

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- API Key de Google Gemini
- 4GB RAM mínimo
- 2GB espacio en disco

### Instalación Rápida
```bash
# 1. Clonar repositorio
git clone <repository-url>
cd keep-coding-final

# 2. Configurar entorno
python setup.py

# 3. Configurar API key
cp .env.example .env
# Editar .env con tu API key de Google

# 4. Verificar instalación
python -m pytest tests/ -v
```

### Configuración Detallada
```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear estructura de directorios
mkdir -p data/{raw,processed,chroma_db}
mkdir -p logs
mkdir -p scripts

# Configurar variables de entorno
export GOOGLE_API_KEY="tu-api-key-aqui"
```

## 🏃‍♂️ Uso Rápido

### 1. Validar Embeddings
```bash
python scripts/validate_embeddings.py
```

### 2. Indexar Documentos
```bash
python scripts/index_documents.py
```

### 3. Probar Consultas Interactivas
```bash
python scripts/interactive_query.py
```

### 4. Ejecutar Evaluación Completa
```bash
python scripts/run_integration_tests.py
```

## 📊 Estructura del Proyecto

```
keep-coding-final/
├── src/
│   ├── chunking/          # Sistema de chunking
│   ├── indexing/          # Indexación en ChromaDB
│   ├── query/             # Manejo de consultas
│   ├── testing/           # Testing y evaluación
│   └── utils/             # Utilidades
├── data/
│   ├── chroma_db/         # Base vectorial
│   ├── raw/               # Datos originales
│   └── processed/         # Datos procesados
├── tests/
│   ├── unit/              # Tests unitarios
│   └── integration/       # Tests de integración
├── scripts/               # Scripts de ejecución
├── config/                # Configuraciones
├── logs/                  # Logs del sistema
└── roadmap/               # Documentación del roadmap
```

## 🔧 Configuración

### Variables de Entorno
```bash
# .env
GOOGLE_API_KEY=tu-api-key-de-google
GOOGLE_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Configuración de ChromaDB
```python
# config/settings.py
CHROMA_PERSIST_DIRECTORY = "data/chroma_db"
CHROMA_COLLECTION_NAME = "legal_documents"
```

## 📈 Monitoreo y Mantenimiento

### Verificar Estado del Sistema
```bash
python scripts/monitor_system.py
```

### Logs Importantes
- `logs/chunking.log`: Proceso de chunking
- `logs/indexing.log`: Indexación de documentos
- `logs/query.log`: Consultas y respuestas
- `logs/integration_testing.log`: Tests de integración

### Métricas de Rendimiento
- **Tiempo de respuesta**: < 5 segundos
- **Tasa de éxito**: > 80%
- **Calidad promedio**: > 3.5/5
- **Chunks indexados**: Según volumen de datos

## 🧪 Testing

### Tests Unitarios
```bash
python -m pytest tests/unit/ -v
```

### Tests de Integración
```bash
python -m pytest tests/integration/ -v
```

### Evaluación Cualitativa
```bash
python scripts/evaluate_queries.py
```

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Error de API Key
```
Error: Invalid API key
```
**Solución**: Verificar que `GOOGLE_API_KEY` esté configurada correctamente en `.env`

#### 2. Error de Embeddings
```
Error: Model not found
```
**Solución**: Verificar conexión a internet y reinstalar `sentence-transformers`

#### 3. Error de ChromaDB
```
Error: Collection not found
```
**Solución**: Ejecutar `python scripts/index_documents.py` para recrear la colección

#### 4. Respuestas Lentas
**Solución**: Verificar configuración de `n_results` y optimizar consultas

### Logs de Debug
```bash
# Ver logs en tiempo real
tail -f logs/query.log

# Ver errores específicos
grep "ERROR" logs/*.log
```

## 📚 Documentación Técnica

### Arquitectura del Sistema
```
Usuario → Query Handler → Filter Extractor → ChromaDB → Gemini → Respuesta
                    ↓
                Chunking → Indexing → Vector Search
```

### Flujo de Datos
1. **Ingesta**: CSV + JSON → Chunking → Embeddings → ChromaDB
2. **Consulta**: Texto → Filtros → Búsqueda Híbrida → Gemini → Respuesta
3. **Trazabilidad**: Fuente visible en cada respuesta

### Componentes Principales

#### DocumentChunker
- División por párrafos naturales
- Fallback recursivo para chunks grandes
- Overlap de 50 tokens entre chunks
- Preservación de metadatos

#### ChromaIndexer
- Normalización de metadatos
- Generación de embeddings
- Indexación con filtros
- Búsqueda híbrida

#### QueryHandler
- Extracción de filtros mejorada
- Prompt estructurado para Gemini
- Trazabilidad automática
- Manejo de errores robusto

## 🚀 Despliegue en Producción

### Requisitos de Producción
- **CPU**: 4+ cores
- **RAM**: 8GB mínimo, 16GB recomendado
- **Almacenamiento**: 10GB+ para datos y embeddings
- **Red**: Conexión estable a APIs de Google

### Configuración de Producción
```bash
# Variables de entorno para producción
export GOOGLE_API_KEY="production-key"
export LOG_LEVEL="INFO"
export MAX_CONCURRENT_QUERIES=10
export CHUNK_SIZE=512
export CHUNK_OVERLAP=50
```

### Monitoreo de Producción
```bash
# Script de monitoreo automático
python scripts/monitor_system.py

# Verificar métricas
python scripts/run_integration_tests.py
```

### Backup y Recuperación
```bash
# Backup de ChromaDB
cp -r data/chroma_db/ backup/chroma_db_$(date +%Y%m%d)

# Restaurar desde backup
cp -r backup/chroma_db_20250101/ data/chroma_db/
```

## 🤝 Contribución

### Desarrollo
1. Fork el repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Testing
```bash
# Ejecutar todos los tests
python -m pytest tests/ -v --cov=src

# Generar reporte de cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte
- **Issues**: Crear issue en GitHub
- **Documentación**: Ver `roadmap/` para detalles técnicos
- **Contacto**: [email@ejemplo.com]

## 🎯 Roadmap Futuro
- [ ] Interfaz web con Streamlit
- [ ] API REST completa
- [ ] Autenticación y autorización
- [ ] Escalabilidad horizontal
- [ ] Análisis avanzado de documentos
- [ ] Integración con sistemas legales existentes
```

### 2. Crear Guía de Usuario
Crear `docs/USER_GUIDE.md`:
```markdown
# Guía de Usuario - Sistema RAG de Expedientes Jurídicos

## 🎯 Introducción
Esta guía te ayudará a usar el sistema RAG para consultar expedientes jurídicos de manera inteligente y eficiente.

## 🚀 Primeros Pasos

### 1. Configuración Inicial
```bash
# Verificar que el sistema esté funcionando
python scripts/monitor_system.py
```

### 2. Probar el Sistema
```bash
# Iniciar modo interactivo
python scripts/interactive_query.py
```

## 💬 Tipos de Consultas

### Consultas de Metadatos
- **Demandante**: "¿Cuál es el demandante del expediente?"
- **Demandado**: "¿Quién es el demandado?"
- **Cuantía**: "¿Cuál es la cuantía del embargo?"
- **Fecha**: "¿En qué fecha se dictó la medida?"
- **Tipo de Medida**: "¿Qué tipo de medida se solicitó?"

### Consultas de Contenido
- **Hechos**: "¿Cuáles son los hechos principales del caso?"
- **Fundamentos**: "¿Qué fundamentos jurídicos se esgrimen?"
- **Medidas**: "¿Cuáles son las medidas cautelares solicitadas?"
- **Pruebas**: "¿Qué pruebas se presentaron?"
- **Estado**: "¿Cuál es el estado actual del proceso?"

### Consultas de Resumen
- **Resumen General**: "Resume el expediente RCCI2150725310"
- **Situación Actual**: "¿Cuál es la situación actual del proceso?"
- **Decisión**: "¿Qué decisión se tomó en el expediente?"
- **Puntos Principales**: "¿Cuáles son los puntos principales del caso?"

## 🔍 Consejos para Consultas Efectivas

### 1. Sé Específico
❌ "¿Qué dice el expediente?"
✅ "¿Cuál es el demandante del expediente RCCI2150725310?"

### 2. Usa Nombres Completos
❌ "embargos de Juan"
✅ "embargos de Juan Pérez"

### 3. Incluye Contexto
❌ "¿Cuál es la fecha?"
✅ "¿En qué fecha se dictó la medida cautelar?"

### 4. Usa Términos Jurídicos
- "demandante" en lugar de "actor"
- "medida cautelar" en lugar de "medida"
- "fundamentos jurídicos" en lugar de "razones"

## 📊 Interpretación de Respuestas

### Estructura de Respuesta
```
[Respuesta del sistema]

Fuente: RCCI2150725310, Chunk 2 de 5
```

### Información de Fuente
- **Documento**: ID del expediente
- **Chunk**: Fragmento específico del documento
- **Posición**: Ubicación exacta de la información

### Calidad de Respuesta
- **Excelente (4-5)**: Información completa y precisa
- **Buena (3-4)**: Información relevante pero incompleta
- **Aceptable (2-3)**: Información básica presente
- **Pobre (1-2)**: Información insuficiente o errónea

## ⚠️ Limitaciones del Sistema

### 1. Dependencia de Datos
- El sistema solo puede responder sobre documentos indexados
- La calidad depende de la completitud de los datos originales

### 2. Contexto Limitado
- Las respuestas se basan en chunks específicos
- Información dispersa puede no ser capturada completamente

### 3. Lenguaje Natural
- El sistema funciona mejor con consultas claras y específicas
- Consultas ambiguas pueden generar respuestas imprecisas

## 🔧 Solución de Problemas

### Respuesta "No se encuentra"
**Causa**: La información no está en los documentos indexados
**Solución**: 
- Verificar que el documento esté indexado
- Reformular la consulta con términos diferentes
- Usar consultas más generales

### Respuesta Lenta
**Causa**: Consulta compleja o sistema sobrecargado
**Solución**:
- Simplificar la consulta
- Esperar unos segundos y reintentar
- Verificar conectividad a internet

### Respuesta Imprecisa
**Causa**: Consulta ambigua o datos incompletos
**Solución**:
- Reformular la consulta de manera más específica
- Usar términos jurídicos exactos
- Incluir más contexto en la consulta

## 📈 Mejores Prácticas

### 1. Consultas Efectivas
- Usa términos específicos del dominio legal
- Incluye nombres completos cuando sea posible
- Especifica el tipo de información que buscas

### 2. Interpretación de Resultados
- Siempre verifica la fuente de la información
- Considera el contexto del chunk específico
- Evalúa la calidad de la respuesta

### 3. Trabajo con Grandes Volúmenes
- Usa filtros específicos para reducir resultados
- Combina consultas para obtener información completa
- Documenta las consultas exitosas para reutilización

## 📞 Soporte

### Recursos de Ayuda
- **Documentación Técnica**: Ver `README.md`
- **Ejemplos de Consultas**: Ver `scripts/interactive_query.py`
- **Logs del Sistema**: Ver `logs/query.log`

### Reportar Problemas
1. Documenta la consulta exacta
2. Incluye la respuesta recibida
3. Especifica el comportamiento esperado
4. Adjunta logs relevantes si es posible

## 🎯 Próximas Mejoras
- Interfaz web más intuitiva
- Sugerencias de consultas automáticas
- Historial de consultas
- Exportación de resultados
- Integración con sistemas legales existentes
```

### 3. Crear Guía de Despliegue
Crear `docs/DEPLOYMENT_GUIDE.md`:
```markdown
# Guía de Despliegue - Sistema RAG

## 🎯 Objetivo
Esta guía proporciona instrucciones detalladas para desplegar el sistema RAG en diferentes entornos.

## 📋 Requisitos del Sistema

### Mínimos
- **CPU**: 4 cores
- **RAM**: 8GB
- **Almacenamiento**: 10GB
- **Red**: Conexión estable a internet
- **OS**: Linux/Ubuntu 20.04+ o macOS 10.15+

### Recomendados
- **CPU**: 8+ cores
- **RAM**: 16GB
- **Almacenamiento**: 50GB SSD
- **Red**: Conexión de alta velocidad
- **OS**: Ubuntu 22.04 LTS

## 🚀 Despliegue Local

### 1. Preparación del Entorno
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.8+
sudo apt install python3.8 python3.8-venv python3.8-dev

# Instalar dependencias del sistema
sudo apt install build-essential git curl

# Crear entorno virtual
python3.8 -m venv rag_env
source rag_env/bin/activate
```

### 2. Instalación del Proyecto
```bash
# Clonar repositorio
git clone <repository-url>
cd keep-coding-final

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API key
```

### 3. Configuración Inicial
```bash
# Ejecutar setup
python setup.py

# Verificar instalación
python -m pytest tests/ -v

# Validar embeddings
python scripts/validate_embeddings.py
```

## 🐳 Despliegue con Docker

### 1. Dockerfile
```dockerfile
FROM python:3.8-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/chroma_db logs

# Exponer puerto (si se implementa API)
EXPOSE 8000

# Comando por defecto
CMD ["python", "scripts/monitor_system.py"]
```

### 2. Docker Compose
```yaml
version: '3.8'

services:
  rag-system:
    build: .
    container_name: rag-system
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PYTHONPATH=/app
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "8000:8000"
    restart: unless-stopped

  # Base de datos opcional
  postgres:
    image: postgres:13
    container_name: rag-postgres
    environment:
      - POSTGRES_DB=rag_db
      - POSTGRES_USER=rag_user
      - POSTGRES_PASSWORD=rag_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. Despliegue con Docker
```bash
# Construir imagen
docker build -t rag-system .

# Ejecutar contenedor
docker run -d \
  --name rag-system \
  -e GOOGLE_API_KEY=tu-api-key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  rag-system

# Ver logs
docker logs rag-system
```

## ☁️ Despliegue en la Nube

### AWS EC2

#### 1. Configurar Instancia
```bash
# Conectar a instancia
ssh -i key.pem ubuntu@your-instance-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install python3.8 python3.8-venv python3.8-dev build-essential git
```

#### 2. Desplegar Aplicación
```bash
# Clonar repositorio
git clone <repository-url>
cd keep-coding-final

# Crear entorno virtual
python3.8 -m venv rag_env
source rag_env/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export GOOGLE_API_KEY="tu-api-key"
```

#### 3. Configurar Servicio
```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/rag-system.service
```

```ini
[Unit]
Description=RAG System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/keep-coding-final
Environment=PATH=/home/ubuntu/keep-coding-final/rag_env/bin
ExecStart=/home/ubuntu/keep-coding-final/rag_env/bin/python scripts/monitor_system.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar servicio
sudo systemctl enable rag-system
sudo systemctl start rag-system
sudo systemctl status rag-system
```

### Google Cloud Platform

#### 1. Configurar VM
```bash
# Crear instancia
gcloud compute instances create rag-system \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud
```

#### 2. Desplegar Aplicación
```bash
# Conectar a instancia
gcloud compute ssh rag-system --zone=us-central1-a

# Seguir pasos similares a AWS EC2
```

### Azure

#### 1. Crear VM
```bash
# Crear grupo de recursos
az group create --name rag-system-rg --location eastus

# Crear VM
az vm create \
  --resource-group rag-system-rg \
  --name rag-system \
  --image UbuntuLTS \
  --size Standard_D4s_v3 \
  --admin-username azureuser
```

## 🔧 Configuración de Producción

### Variables de Entorno
```bash
# .env.production
GOOGLE_API_KEY=production-api-key
GOOGLE_MODEL=gemini-2.0-flash-exp
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
LOG_LEVEL=INFO
MAX_CONCURRENT_QUERIES=10
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db
```

### Configuración de Logging
```python
# config/logging.py
import logging
import os

def setup_production_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/app/logs/rag_system.log'),
            logging.StreamHandler()
        ]
    )
```

### Monitoreo de Producción
```bash
# Script de monitoreo automático
#!/bin/bash
# /usr/local/bin/monitor_rag.sh

while true; do
    python /app/scripts/monitor_system.py
    sleep 300  # Cada 5 minutos
done
```

## 🔒 Seguridad

### API Keys
```bash
# Usar variables de entorno
export GOOGLE_API_KEY="tu-api-key"

# O usar archivo .env (no committear)
echo "GOOGLE_API_KEY=tu-api-key" > .env
```

### Firewall
```bash
# Configurar firewall (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 8000  # Si se implementa API
sudo ufw enable
```

### SSL/TLS
```bash
# Instalar certificados SSL
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com
```

## 📊 Monitoreo y Mantenimiento

### Métricas Clave
- **Tiempo de respuesta**: < 5 segundos
- **Tasa de éxito**: > 80%
- **Uso de memoria**: < 80%
- **Espacio en disco**: < 90%

### Logs Importantes
```bash
# Ver logs en tiempo real
tail -f /app/logs/query.log

# Ver errores
grep "ERROR" /app/logs/*.log

# Ver métricas
python scripts/monitor_system.py
```

### Backup
```bash
# Script de backup automático
#!/bin/bash
# /usr/local/bin/backup_rag.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/rag_system"

# Crear backup
mkdir -p $BACKUP_DIR
cp -r /app/data/chroma_db $BACKUP_DIR/chroma_db_$DATE
cp -r /app/logs $BACKUP_DIR/logs_$DATE

# Limpiar backups antiguos (mantener últimos 7 días)
find $BACKUP_DIR -name "chroma_db_*" -mtime +7 -delete
find $BACKUP_DIR -name "logs_*" -mtime +7 -delete
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Memoria
```
OutOfMemoryError: Java heap space
```
**Solución**: Aumentar memoria de JVM o optimizar consultas

#### 2. Error de API
```
API key invalid or quota exceeded
```
**Solución**: Verificar API key y límites de cuota

#### 3. Error de ChromaDB
```
Collection not found
```
**Solución**: Recrear colección con `python scripts/index_documents.py`

#### 4. Respuestas Lentas
**Solución**: 
- Optimizar consultas
- Aumentar recursos del sistema
- Implementar caché

### Logs de Debug
```bash
# Habilitar debug logging
export LOG_LEVEL=DEBUG

# Ver logs detallados
tail -f /app/logs/*.log | grep DEBUG
```

## 📈 Escalabilidad

### Horizontal
- Implementar balanceador de carga
- Usar múltiples instancias
- Compartir base de datos

### Vertical
- Aumentar CPU y RAM
- Usar SSD para almacenamiento
- Optimizar consultas

### Optimizaciones
- Implementar caché Redis
- Comprimir embeddings
- Usar índices optimizados

## 🔄 Actualizaciones

### Proceso de Actualización
```bash
# 1. Backup
python scripts/backup_system.py

# 2. Actualizar código
git pull origin main

# 3. Actualizar dependencias
pip install -r requirements.txt

# 4. Migrar datos si es necesario
python scripts/migrate_data.py

# 5. Verificar sistema
python scripts/run_integration_tests.py

# 6. Reiniciar servicio
sudo systemctl restart rag-system
```

### Rollback
```bash
# Revertir a versión anterior
git checkout <previous-commit>

# Restaurar backup
python scripts/restore_backup.py

# Reiniciar servicio
sudo systemctl restart rag-system
```
```

## ✅ Criterios de Éxito
- [ ] README completo y claro
- [ ] Guía de usuario detallada
- [ ] Guía de despliegue para múltiples entornos
- [ ] Documentación de troubleshooting
- [ ] Scripts de monitoreo y backup
- [ ] Configuraciones de producción
- [ ] Guías de escalabilidad

## 🔍 Verificación
Ejecutar los siguientes comandos:
```bash
# Verificar documentación
ls -la docs/
cat README.md | head -20

# Probar scripts de monitoreo
python scripts/monitor_system.py

# Verificar configuración
python -c "from config.settings import *; print('✅ Configuración cargada')"
```

## 📊 Métricas de Documentación
- **Completitud**: 100% de componentes documentados
- **Claridad**: Instrucciones paso a paso
- **Troubleshooting**: Soluciones para problemas comunes
- **Escalabilidad**: Guías para crecimiento

## 📝 Notas Importantes
- La documentación debe ser mantenida actualizada
- Los scripts de monitoreo son críticos para producción
- El backup automático es esencial
- La seguridad debe ser prioritaria en producción 