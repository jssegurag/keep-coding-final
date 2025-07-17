# 🎨 Interfaz de Usuario Streamlit - Sistema RAG Legal

## 📋 Descripción

La interfaz de usuario del sistema RAG Legal está construida con **Streamlit** y está diseñada específicamente para abogados que procesan oficios jurídicos en Colombia. Proporciona una experiencia de usuario intuitiva y eficiente para interactuar con el sistema de Recuperación Augmentada por Generación.

## 🏗️ Arquitectura

### Estructura del Paquete

```
src/interface/
├── __init__.py          # Inicialización del paquete
├── config.py            # Configuración de la aplicación
├── api_client.py        # Cliente para comunicarse con la API
├── components.py        # Componentes reutilizables de UI
├── pages.py            # Páginas específicas de cada módulo
├── app.py              # Aplicación principal
└── README.md           # Esta documentación
```

### Principios de Diseño

- **Separación de Responsabilidades**: Cada módulo tiene una responsabilidad específica
- **Reutilización de Componentes**: Componentes modulares y reutilizables
- **Configuración Centralizada**: Todas las configuraciones en un solo lugar
- **Manejo de Errores**: Gestión robusta de errores y excepciones
- **Experiencia de Usuario**: Interfaz intuitiva para abogados

## 🚀 Funcionalidades

### 1. 🏠 Página de Inicio
- **Información del Sistema**: Estado de conexión y métricas básicas
- **Descripción del Propósito**: Explicación clara del sistema RAG
- **Casos de Uso Específicos**: Oficios de embargo, desembargo, sentencias
- **Estadísticas Rápidas**: Métricas de rendimiento del sistema

### 2. 🔍 Consultas Semánticas
- **Consulta Individual**: Formulario para consultas en lenguaje natural
- **Consultas en Lote**: Procesamiento eficiente de múltiples consultas
- **Extracción de Entidades**: Identificación automática de personas, organizaciones, fechas
- **Resultados Enriquecidos**: Información detallada con fuentes y confianza

### 3. 📊 Historial de Consultas
- **Trazabilidad Completa**: Registro de todas las consultas realizadas
- **Información Detallada**: Respuestas, entidades, fuentes utilizadas
- **Paginación**: Navegación a través del historial
- **Análisis de Patrones**: Identificación de consultas frecuentes

### 4. ⚙️ Configuración del Sistema
- **Estado del Sistema**: Monitoreo en tiempo real
- **Configuración de API**: URLs, timeouts, parámetros
- **Estadísticas Detalladas**: Métricas de rendimiento y uso
- **Información Técnica**: Detalles de implementación

### 5. 📚 Gestión de Documentos
- **Estado**: Funcionalidad en desarrollo
- **Disponibilidad**: Requiere datos CSV no disponibles en MVP
- **Próximas versiones**: Gestión completa de documentos

## 🎯 Casos de Uso Específicos

### Oficios de Embargo
- **Identificación de Demandantes**: Extracción automática de información del demandante
- **Identificación de Demandados**: Lista completa de personas embargadas
- **Montos y Bienes**: Información detallada sobre embargos
- **Tribunales Emisores**: Identificación de la autoridad judicial

### Oficios de Desembargo
- **Búsqueda por Cédula**: Localización rápida por número de identificación
- **Búsqueda por Expediente**: Consulta por número de expediente
- **Historial de Procesos**: Seguimiento completo del caso
- **Validación de Información**: Verificación de datos para desembargo

### Análisis de Sentencias
- **Extracción de Decisiones**: Identificación de resoluciones judiciales
- **Partes Involucradas**: Demandantes, demandados, abogados
- **Medidas Cautelares**: Identificación de medidas solicitadas
- **Fechas y Plazos**: Información temporal del proceso

## 🛠️ Tecnologías Utilizadas

### Frontend
- **Streamlit**: Framework principal para la interfaz de usuario
- **CSS Personalizado**: Estilos específicos para el dominio legal
- **Pandas**: Manipulación y visualización de datos
- **Requests**: Comunicación con la API REST

### Backend Integration
- **FastAPI**: API REST para el backend
- **Pydantic**: Validación de datos y serialización
- **Uvicorn**: Servidor ASGI para la API

### Características Especiales
- **Responsive Design**: Adaptable a diferentes tamaños de pantalla
- **Error Handling**: Manejo robusto de errores y excepciones
- **Loading States**: Indicadores de carga para mejor UX
- **Session Management**: Gestión de estado de la sesión

## 🚀 Instalación y Ejecución

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar Sistema Completo
```bash
python run_system.py
```

### 3. Ejecutar Solo la Interfaz
```bash
streamlit run streamlit_app.py
```

### 4. Ejecutar Solo la API
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📊 URLs de Acceso

- **Interfaz de Usuario**: http://localhost:8501
- **API REST**: http://localhost:8001
- **Documentación API**: http://localhost:8001/docs
- **API ReDoc**: http://localhost:8001/redoc

## 🎨 Personalización

### Configuración de Estilos
Los estilos se pueden personalizar en `components.py`:

```python
# Colores específicos para documentos legales
sentencia_color: str = "#2E8B57"  # Verde mar
demanda_color: str = "#DC143C"    # Carmesí
recurso_color: str = "#FF8C00"    # Naranja oscuro
```

### Configuración de la API
La configuración de la API se puede modificar en `config.py`:

```python
@dataclass
class APIConfig:
    base_url: str = "http://localhost:8001"
    timeout: int = 30
```

### Tipos de Documentos
Los tipos de documentos se pueden personalizar en `config.py`:

```python
document_types = {
    "Sentencia": "Decisiones judiciales finales",
    "Demanda": "Documentos de inicio de proceso",
    "Recurso": "Apelaciones y recursos",
    # ... más tipos
}
```

## 🔧 Desarrollo

### Estructura de Desarrollo
1. **Configuración**: Modificar `config.py` para cambios de configuración
2. **Componentes**: Agregar nuevos componentes en `components.py`
3. **Páginas**: Crear nuevas páginas en `pages.py`
4. **API Client**: Extender funcionalidad en `api_client.py`

### Buenas Prácticas
- **Separación de Responsabilidades**: Cada módulo tiene una función específica
- **Manejo de Errores**: Siempre incluir try-catch para operaciones críticas
- **Documentación**: Comentar funciones y clases importantes
- **Testing**: Probar componentes individualmente
- **Performance**: Optimizar consultas y renderizado

### Debugging
Para activar el modo debug:

```python
# En app.py
if st.checkbox("Mostrar información de debug"):
    st.exception(e)
```

## 📈 Métricas y Monitoreo

### Métricas de Usuario
- **Consultas por Sesión**: Número de consultas realizadas
- **Tiempo de Respuesta**: Latencia de las consultas
- **Tipos de Consulta**: Análisis de patrones de uso
- **Documentos Consultados**: Frecuencia de acceso a documentos

### Métricas del Sistema
- **Estado de la API**: Disponibilidad y respuesta
- **Uso de Recursos**: CPU, memoria, almacenamiento
- **Errores**: Frecuencia y tipos de errores
- **Performance**: Tiempos de respuesta y throughput

## 🔒 Seguridad

### Consideraciones de Seguridad
- **Validación de Entrada**: Todas las entradas se validan
- **Sanitización**: Datos se limpian antes de procesar
- **Rate Limiting**: Límites en consultas por usuario
- **Logging**: Registro de actividades para auditoría

### Próximas Mejoras de Seguridad
- **Autenticación**: Sistema de login para usuarios
- **Autorización**: Roles y permisos específicos
- **Encriptación**: Datos sensibles encriptados
- **Auditoría**: Logs detallados de actividades

## 🚀 Roadmap

### Versión 1.1
- [ ] Gráficos interactivos con Plotly
- [ ] Exportación de resultados a PDF
- [ ] Búsqueda avanzada con filtros múltiples
- [ ] Notificaciones en tiempo real

### Versión 1.2
- [ ] Autenticación de usuarios
- [ ] Roles y permisos
- [ ] Dashboard ejecutivo
- [ ] Integración con sistemas externos

### Versión 1.3
- [ ] Análisis predictivo
- [ ] Machine Learning para clasificación
- [ ] API para integraciones externas
- [ ] Mobile responsive design

## 📞 Soporte

Para soporte técnico o preguntas sobre la interfaz de usuario:

1. **Documentación**: Revisar esta documentación
2. **Issues**: Crear issue en el repositorio
3. **Logs**: Revisar logs de la aplicación
4. **Debug**: Activar modo debug para más información

## 📄 Licencia

Este proyecto es parte del sistema RAG Legal y está sujeto a los mismos términos de licencia del proyecto principal. 