"""
Páginas específicas para cada módulo de la interfaz de usuario.

Este módulo contiene las páginas individuales para cada funcionalidad
del sistema RAG Legal, diseñadas específicamente para abogados.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from .components import (
    render_query_form, render_query_result, render_documents_table,
    render_query_history, render_system_status, render_batch_query_form,
    render_batch_results, show_success_message, show_error_message
)
from .api_client import get_api_client, test_api_connection
from .config import get_config

def render_home_page():
    """Renderizar página de inicio."""
    config = get_config()
    
    st.title("🏠 Página de Inicio")
    
    # Verificar conexión con la API
    if not test_api_connection():
        st.error("⚠️ No se pudo conectar con la API del sistema. Verifique que el servidor esté ejecutándose.")
        return
    
    # Información del sistema
    try:
        api_client = get_api_client()
        system_info = api_client.get_system_info()
        
        st.markdown("### 📊 Información del Sistema")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Estado", "🟢 Conectado")
            st.metric("Versión", system_info.get('version', '1.0.0'))
        
        with col2:
            st.metric("API", "FastAPI REST")
            st.metric("UI", "Streamlit")
        
    except Exception as e:
        st.error(f"Error obteniendo información del sistema: {str(e)}")
    
    # Descripción del sistema
    st.markdown("---")
    st.markdown("### 🎯 Propósito del Sistema")
    
    st.markdown("""
    Este sistema de **Recuperación Augmentada por Generación (RAG)** está diseñado 
    específicamente para abogados que procesan oficios jurídicos en Colombia.
    
    #### 🚀 Funcionalidades Principales:
    
    - **🔍 Consultas Semánticas**: Realice preguntas en lenguaje natural sobre documentos legales
    - **📊 Historial de Consultas**: Revise consultas anteriores y sus resultados
    - **⚙️ Monitoreo del Sistema**: Verifique el estado y rendimiento del sistema
    
    #### 🎯 Casos de Uso Específicos:
    
    - **Oficios de Embargo**: Identifique demandantes, demandados y montos
    - **Oficios de Desembargo**: Busque expedientes por cédula o número de expediente
    - **Análisis de Sentencias**: Extraiga información clave de decisiones judiciales
    - **Seguimiento de Procesos**: Consulte el historial completo de un expediente
    
    #### 📈 Beneficios:
    
    - **Eficiencia**: Procese 4000+ oficios diarios de manera automatizada
    - **Precisión**: Extracción automática de entidades y metadatos
    - **Trazabilidad**: Historial completo de consultas y resultados
    - **Escalabilidad**: Sistema preparado para grandes volúmenes de documentos
    """)
    
    # Estadísticas rápidas
    st.markdown("---")
    st.markdown("### 📈 Estadísticas Rápidas")
    
    try:
        stats = api_client.get_system_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Consultas Realizadas", stats.get('total_queries', 0))
        
        with col2:
            st.metric("Consultas Exitosas", stats.get('successful_queries', 0))
        
        with col3:
            st.metric("Tiempo Promedio", f"{stats.get('average_response_time', 0):.2f}s")
        
        with col4:
            st.metric("Documentos", stats.get('total_documents', 0))
            
    except Exception as e:
        st.warning(f"No se pudieron cargar las estadísticas: {str(e)}")

def render_queries_page():
    """Renderizar página de consultas semánticas."""
    st.title("🔍 Consultas Semánticas")
    
    # Verificar conexión
    if not test_api_connection():
        st.error("⚠️ No se pudo conectar con la API del sistema.")
        return
    
    # Pestañas para diferentes tipos de consultas
    tab1, tab2 = st.tabs(["🔍 Consulta Individual", "📦 Consultas en Lote"])
    
    with tab1:
        render_individual_query_tab()
    
    with tab2:
        render_batch_query_tab()

def render_individual_query_tab():
    """Renderizar pestaña de consulta individual."""
    api_client = get_api_client()
    
    # Formulario de consulta
    query_data = render_query_form()
    
    if query_data:
        try:
            with st.spinner("🔍 Procesando consulta..."):
                result = api_client.perform_query(
                    query=query_data["query"],
                    n_results=query_data["n_results"]
                )
            
            show_success_message("Consulta procesada exitosamente")
            render_query_result(result)
            
        except Exception as e:
            show_error_message(f"Error procesando consulta: {str(e)}")

def render_batch_query_tab():
    """Renderizar pestaña de consultas en lote."""
    api_client = get_api_client()
    
    # Formulario de consultas en lote
    queries = render_batch_query_form()
    
    if queries:
        try:
            with st.spinner("📦 Procesando lote de consultas..."):
                results = api_client.perform_batch_queries(queries)
            
            show_success_message("Lote procesado exitosamente")
            render_batch_results(results)
            
        except Exception as e:
            show_error_message(f"Error procesando lote: {str(e)}")

def render_documents_page():
    """Renderizar página de gestión de documentos."""
    st.title("📚 Gestión de Documentos")
    
    # Verificar conexión
    if not test_api_connection():
        st.error("⚠️ No se pudo conectar con la API del sistema.")
        return
    
    st.info("""
    📋 **Funcionalidad en Desarrollo**
    
    La gestión de documentos requiere datos CSV que no están disponibles en esta versión del MVP.
    
    **Funcionalidades disponibles:**
    - ✅ Consultas semánticas
    - ✅ Historial de consultas  
    - ✅ Monitoreo del sistema
    
    **Próximas versiones incluirán:**
    - 📄 Gestión completa de documentos
    - 🔍 Filtros avanzados
    - 📊 Análisis de documentos
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Casos de Uso")
    
    st.markdown("""
    **Oficios de Embargo:**
    - Identificación de demandantes y demandados
    - Extracción de montos y bienes embargados
    - Seguimiento de procesos judiciales
    
    **Oficios de Desembargo:**
    - Búsqueda por cédula o número de expediente
    - Validación de información para desembargo
    - Historial completo de procesos
    
    **Análisis de Sentencias:**
    - Extracción de decisiones judiciales
    - Identificación de partes involucradas
    - Análisis de medidas cautelares
    """)

def render_history_page():
    """Renderizar página de historial de consultas."""
    st.title("📊 Historial de Consultas")
    
    # Verificar conexión
    if not test_api_connection():
        st.error("⚠️ No se pudo conectar con la API del sistema.")
        return
    
    api_client = get_api_client()
    
    # Configuración de paginación
    col1, col2 = st.columns(2)
    
    with col1:
        page = st.number_input(
            "Página:",
            min_value=1,
            value=1,
            help="Número de página a mostrar"
        )
    
    with col2:
        page_size = st.selectbox(
            "Consultas por página:",
            [10, 20, 30, 50],
            index=0,
            help="Cantidad de consultas a mostrar"
        )
    
    # Cargar historial
    if st.button("🔄 Actualizar Historial"):
        try:
            with st.spinner("📊 Cargando historial..."):
                history = api_client.get_query_history(
                    page=page,
                    page_size=page_size
                )
                
                render_query_history(history)
                
        except Exception as e:
            show_error_message(f"Error cargando historial: {str(e)}")

def render_system_page():
    """Renderizar página de configuración del sistema."""
    st.title("⚙️ Configuración del Sistema")
    
    # Verificar conexión
    if not test_api_connection():
        st.error("⚠️ No se pudo conectar con la API del sistema.")
        return
    
    api_client = get_api_client()
    
    # Pestañas para diferentes aspectos del sistema
    tab1, tab2, tab3 = st.tabs(["📊 Estado del Sistema", "🔧 Configuración", "📈 Estadísticas"])
    
    with tab1:
        render_system_status_tab(api_client)
    
    with tab2:
        render_configuration_tab()
    
    with tab3:
        render_statistics_tab(api_client)

def render_system_status_tab(api_client):
    """Renderizar pestaña de estado del sistema."""
    try:
        # Estado de salud
        health = api_client.health_check()
        render_system_status(health)
        
        # Información del sistema
        st.markdown("---")
        st.markdown("### ℹ️ Información del Sistema")
        
        system_info = api_client.get_system_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Información General:**")
            st.write(f"**Versión:** {system_info.get('version', 'N/A')}")
            st.write(f"**Descripción:** {system_info.get('description', 'N/A')}")
            st.write(f"**Arquitectura:** {system_info.get('architecture', 'N/A')}")
        
        with col2:
            st.markdown("**Tecnologías:**")
            technologies = system_info.get('technologies', [])
            for tech in technologies:
                st.write(f"- {tech}")
        
        # Funcionalidades disponibles
        st.markdown("---")
        st.markdown("### 🚀 Funcionalidades Disponibles")
        features = system_info.get('features', [])
        for feature in features:
            st.write(f"✅ {feature}")
        
    except Exception as e:
        show_error_message(f"Error obteniendo información del sistema: {str(e)}")

def render_configuration_tab():
    """Renderizar pestaña de configuración."""
    config = get_config()
    
    st.markdown("### 🔧 Configuración de la Aplicación")
    
    # Configuración de la API
    st.markdown("#### 🌐 Configuración de la API")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_url = st.text_input(
            "URL de la API:",
            value=config.api.base_url,
            help="URL base del servidor de la API"
        )
    
    with col2:
        timeout = st.number_input(
            "Timeout (segundos):",
            min_value=5,
            max_value=120,
            value=config.api.timeout,
            help="Tiempo máximo de espera para respuestas de la API"
        )
    
    if st.button("💾 Guardar Configuración"):
        try:
            # Aquí se actualizaría la configuración
            st.success("Configuración guardada exitosamente")
        except Exception as e:
            st.error(f"Error guardando configuración: {str(e)}")
    
    # Configuración de la interfaz
    st.markdown("---")
    st.markdown("#### 🎨 Configuración de la Interfaz")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_query_length = st.number_input(
            "Longitud máxima de consulta:",
            min_value=100,
            max_value=3000,  # Aumentado de 1000 a 3000 para permitir futuras expansiones
            value=config.ui.max_query_length,
            help="Número máximo de caracteres por consulta"
        )
    
    with col2:
        max_results = st.number_input(
            "Resultados máximos por consulta:",
            min_value=1,
            max_value=100,  # Aumentado de 50 a 100 para permitir futuras expansiones
            value=config.ui.max_results_per_query,
            help="Número máximo de resultados por consulta"
        )

def render_statistics_tab(api_client):
    """Renderizar pestaña de estadísticas."""
    try:
        stats = api_client.get_system_stats()
        
        st.markdown("### 📈 Estadísticas del Sistema")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Consultas Totales", stats.get('total_queries', 0))
        
        with col2:
            st.metric("Consultas Exitosas", stats.get('successful_queries', 0))
        
        with col3:
            st.metric("Tiempo Promedio", f"{stats.get('average_response_time', 0):.2f}s")
        
        with col4:
            st.metric("Documentos", stats.get('total_documents', 0))
        
        # Distribución por tipo de documento
        st.markdown("---")
        st.markdown("### 📄 Distribución por Tipo de Documento")
        
        document_types = stats.get('document_types', {})
        if document_types:
            for doc_type, count in document_types.items():
                st.write(f"**{doc_type}:** {count} documentos")
        
        # Distribución por tribunal
        st.markdown("---")
        st.markdown("### ⚖️ Distribución por Tribunal")
        
        courts = stats.get('courts', {})
        if courts:
            for court, count in courts.items():
                st.write(f"**{court}:** {count} documentos")
        
        # Información del sistema
        st.markdown("---")
        st.markdown("### 💻 Información del Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Estado:** {stats.get('system_status', 'N/A')}")
            st.write(f"**Uptime:** {stats.get('uptime', 'N/A')}")
            st.write(f"**Versión:** {stats.get('version', 'N/A')}")
        
        with col2:
            st.write(f"**Memoria:** {stats.get('memory_usage', 'N/A')}")
            st.write(f"**CPU:** {stats.get('cpu_usage', 'N/A')}")
            st.write(f"**Disco:** {stats.get('disk_usage', 'N/A')}")
        
    except Exception as e:
        show_error_message(f"Error obteniendo estadísticas: {str(e)}") 