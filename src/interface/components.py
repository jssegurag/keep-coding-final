"""
Componentes reutilizables para la interfaz de usuario Streamlit.

Este módulo contiene componentes personalizados para la interfaz de usuario,
diseñados específicamente para abogados que procesan oficios jurídicos.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import pandas as pd
from .config import get_config

def render_header():
    """Renderizar el encabezado principal de la aplicación."""
    config = get_config()
    
    st.set_page_config(
        page_title=config.ui.page_title,
        page_icon=config.ui.page_icon,
        layout=config.ui.layout,
        initial_sidebar_state=config.ui.initial_sidebar_state
    )
    
    # CSS personalizado para mejorar la apariencia
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .legal-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .entity-tag {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
    }
    .success-message {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-message {
        background: #ffebee;
        border: 1px solid #f44336;
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="main-header">
        <h1>{config.ui.page_title}</h1>
        <p>Sistema de Recuperación Augmentada por Generación para Oficios Jurídicos</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderizar la barra lateral con navegación."""
    config = get_config()
    
    st.sidebar.title("⚖️ Navegación")
    
    # Menú de navegación
    page = st.sidebar.selectbox(
        "Seleccionar módulo:",
        [
            "🏠 Inicio",
            "🔍 Consultas Semánticas", 
            "📊 Historial de Consultas",
            "⚙️ Configuración del Sistema"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Información del sistema
    st.sidebar.subheader("ℹ️ Información del Sistema")
    st.sidebar.markdown("**Versión:** 1.0.0")
    st.sidebar.markdown("**API:** FastAPI REST")
    st.sidebar.markdown("**UI:** Streamlit")
    
    # Tipos de documentos disponibles
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Tipos de Documentos")
    for doc_type, description in config.document_types.items():
        st.sidebar.markdown(f"**{doc_type}:** {description}")
    
    return page

def render_query_form() -> Optional[Dict[str, Any]]:
    """
    Renderizar formulario de consulta semántica.
    
    Returns:
        Diccionario con los datos del formulario o None si no se envió
    """
    config = get_config()
    
    st.subheader("🔍 Consulta Semántica")
    st.markdown("Realice consultas en lenguaje natural sobre los documentos legales.")
    
    with st.form("query_form"):
        # Campo de consulta
        query = st.text_area(
            "Consulta:",
            placeholder="Ej: ¿Cuál es el demandante del expediente ABC-2024-001? ¿Puede proporcionar información detallada sobre las partes involucradas, las fechas importantes del proceso, los montos reclamados y las medidas cautelares solicitadas?",
            max_chars=config.ui.max_query_length,
            help=f"Escriba su consulta en lenguaje natural. El sistema entenderá el contexto legal. Máximo {config.ui.max_query_length} caracteres."
        )
        
        # Configuraciones adicionales
        col1, col2 = st.columns(2)
        
        with col1:
            n_results = st.slider(
                "Número de resultados:",
                min_value=1,
                max_value=config.ui.max_results_per_query,
                value=10,  # Cambiado de 5 a 10 como valor por defecto
                help=f"Cantidad de resultados a mostrar (máximo {config.ui.max_results_per_query})"
            )
        
        with col2:
            include_entities = st.checkbox(
                "Extraer entidades",
                value=True,
                help="Extraer automáticamente personas, organizaciones, fechas, etc."
            )
        
        # Botón de envío
        submitted = st.form_submit_button("🔍 Realizar Consulta")
        
        if submitted and query.strip():
            return {
                "query": query.strip(),
                "n_results": n_results,
                "include_entities": include_entities
            }
    
    return None

def render_query_result(result: Dict[str, Any]):
    """
    Renderizar resultado de consulta con información semántica detallada.
    
    Args:
        result: Resultado de la consulta de la API
    """
    st.subheader("📋 Resultado de la Consulta")
    
    # Información de la estrategia de búsqueda
    search_strategy = result.get('search_strategy', 'unknown')
    search_results_count = result.get('search_results_count', 0)
    
    # Mostrar información de la búsqueda
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estrategia", search_strategy.replace('_', ' ').title())
    with col2:
        st.metric("Chunks Encontrados", search_results_count)
    with col3:
        filters_used = result.get('filters_used', {})
        if filters_used:
            st.metric("Filtros Aplicados", len(filters_used))
        else:
            st.metric("Filtros Aplicados", 0)
    
    # Respuesta principal
    st.markdown("### 🤖 Respuesta Generada")
    st.markdown(f"""
    <div class="legal-card">
        {result.get('response', 'No se encontró respuesta')}
    </div>
    """, unsafe_allow_html=True)
    
    # Resultados semánticos de la búsqueda
    st.markdown("### 🔍 Resultados Semánticos de la Búsqueda")
    
    # Información de fuente
    source_info = result.get('source_info', {})
    if source_info:
        st.markdown("#### 📄 Documentos Fuente")
        documents_used = source_info.get('documents_used', [])
        if documents_used:
            for doc in documents_used:
                st.markdown(f"- **{doc}**")
        
        confidence = source_info.get('confidence_score', 0)
        if confidence:
            st.progress(confidence)
            st.caption(f"Confianza: {confidence:.2%}")
    
    # Mostrar chunks encontrados
    search_results = result.get('search_results', {})
    if search_results:
        metadatas = search_results.get('metadatas', [[]])[0] if search_results.get('metadatas') else []
        documents = search_results.get('documents', [[]])[0] if search_results.get('documents') else []
        distances = search_results.get('distances', [[]])[0] if search_results.get('distances') else []
        
        if metadatas and documents:
            st.markdown("#### 📝 Chunks Encontrados")
            
            for i, (metadata, document, distance) in enumerate(zip(metadatas, documents, distances)):
                with st.expander(f"Chunk {i+1}: {metadata.get('document_id', 'N/A')} - Score: {1-distance:.3f}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**Contenido del Chunk:**")
                        st.text_area(
                            f"Contenido {i+1}",
                            value=document,
                            height=150,
                            key=f"chunk_content_{i}"
                        )
                    
                    with col2:
                        st.markdown("**Metadatos:**")
                        for key, value in metadata.items():
                            if key not in ['chunk_id', 'document_id']:
                                st.write(f"**{key}:** {value}")
                        
                        st.markdown("**Score de Similitud:**")
                        similarity_score = 1 - distance
                        st.progress(similarity_score)
                        st.caption(f"{similarity_score:.3%}")
    
    # Entidades extraídas
    entities = result.get('entities', {})
    if entities:
        st.markdown("### 🏷️ Entidades Identificadas")
        entity_html = ""
        for entity_type, values in entities.items():
            if isinstance(values, list):
                for value in values:
                    entity_html += f'<span class="entity-tag">{entity_type}: {value}</span>'
            else:
                entity_html += f'<span class="entity-tag">{entity_type}: {values}</span>'
        st.markdown(f'<div>{entity_html}</div>', unsafe_allow_html=True)
    
    # Filtros utilizados
    filters_used = result.get('filters_used', {})
    if filters_used:
        st.markdown("### 🔧 Filtros Aplicados")
        for filter_key, filter_value in filters_used.items():
            st.write(f"**{filter_key}:** {filter_value}")
    
    # Metadatos enriquecidos
    enriched_metadata = result.get('enriched_metadata', [])
    if enriched_metadata:
        st.markdown("### 📊 Metadatos Enriquecidos")
        for metadata in enriched_metadata:
            with st.expander(f"Documento {metadata.get('document_id', 'N/A')}"):
                st.write(f"**Relevancia:** {metadata.get('relevance_score', 0):.2%}")
                st.write(f"**Entidades:** {', '.join(metadata.get('extracted_entities', []))}")
                if 'chunk_used' in metadata:
                    st.text_area("Fragmento utilizado:", metadata['chunk_used'], height=100)
    
    # Información temporal
    timestamp = result.get('timestamp', '')
    if timestamp:
        st.markdown("---")
        st.caption(f"Consulta procesada el: {timestamp}")

def render_documents_table(documents: List[Dict[str, Any]], page: int = 1):
    """
    Renderizar tabla de documentos.
    
    Args:
        documents: Lista de documentos
        page: Número de página actual
    """
    config = get_config()
    
    if not documents:
        st.info("No se encontraron documentos que coincidan con los filtros.")
        return
    
    # Crear DataFrame para mejor visualización
    df_data = []
    for doc in documents:
        df_data.append({
            "ID": doc.get('document_id', 'N/A'),
            "Título": doc.get('title', 'Sin título'),
            "Tipo": doc.get('document_type', 'N/A'),
            "Tribunal": doc.get('court', 'N/A'),
            "Expediente": doc.get('case_number', 'N/A'),
            "Fecha": doc.get('date_filed', 'N/A'),
            "Partes": len(doc.get('partes', [])),
            "Fragmentos": doc.get('chunk_count', 0)
        })
    
    df = pd.DataFrame(df_data)
    
    # Mostrar tabla con paginación
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Información de paginación
    st.caption(f"Página {page} - Mostrando {len(documents)} documentos")

def render_query_history(history: Dict[str, Any]):
    """
    Renderizar historial de consultas.
    
    Args:
        history: Datos del historial de consultas
    """
    queries = history.get('queries', [])
    
    if not queries:
        st.info("No hay consultas en el historial.")
        return
    
    st.subheader("📊 Historial de Consultas")
    
    for i, query_data in enumerate(queries):
        with st.expander(f"Consulta {i+1}: {query_data.get('query', 'N/A')[:50]}..."):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Consulta:**")
                st.write(query_data.get('query', 'N/A'))
                
                st.markdown("**Respuesta:**")
                st.write(query_data.get('response', 'N/A'))
            
            with col2:
                st.markdown("**Información:**")
                st.write(f"**Fecha:** {query_data.get('timestamp', 'N/A')}")
                st.write(f"**Resultados:** {query_data.get('search_results_count', 0)}")
                
                entities = query_data.get('entities', {})
                if entities:
                    st.markdown("**Entidades:**")
                    for entity_type, value in entities.items():
                        st.write(f"- {entity_type}: {value}")
    
    # Información de paginación
    total_count = history.get('total_count', 0)
    page = history.get('page', 1)
    page_size = history.get('page_size', 10)
    total_pages = history.get('total_pages', 1)
    
    st.caption(f"Mostrando {len(queries)} de {total_count} consultas (Página {page} de {total_pages})")

def render_system_status(status: Dict[str, Any]):
    """
    Renderizar estado del sistema.
    
    Args:
        status: Información del estado del sistema
    """
    st.subheader("⚙️ Estado del Sistema")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Estado", status.get('status', 'Desconocido'))
    
    with col2:
        st.metric("Documentos", status.get('documents_count', 0))
    
    with col3:
        st.metric("Consultas", status.get('queries_count', 0))
    
    with col4:
        uptime = status.get('uptime', 0)
        st.metric("Tiempo Activo", f"{uptime:.1f}s")
    
    # Información detallada
    with st.expander("Información Detallada"):
        st.json(status)

def render_batch_query_form() -> Optional[List[str]]:
    """
    Renderizar formulario para consultas en lote.
    
    Returns:
        Lista de consultas o None si no se envió
    """
    config = get_config()
    
    st.subheader("📦 Consultas en Lote")
    st.markdown("Realice múltiples consultas de manera eficiente.")
    
    with st.form("batch_query_form"):
        # Campo para múltiples consultas
        queries_text = st.text_area(
            "Consultas (una por línea):",
            placeholder="¿Cuál es el demandante del expediente RCCI2150725385? ¿Puede proporcionar información detallada sobre las partes involucradas?\n¿Qué tribunal emitió la sentencia y cuáles son las fechas importantes?\n¿Cuáles son las medidas cautelares solicitadas y los montos involucrados?",
            help=f"Máximo {config.ui.max_batch_queries} consultas por lote, cada una hasta {config.ui.max_query_length} caracteres"
        )
        
        submitted = st.form_submit_button("📦 Procesar Lote")
        
        if submitted and queries_text.strip():
            queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
            if len(queries) > config.ui.max_batch_queries:
                st.error(f"Máximo {config.ui.max_batch_queries} consultas por lote")
                return None
            return queries
    
    return None

def render_batch_results(results: Dict[str, Any]):
    """
    Renderizar resultados de consultas en lote.
    
    Args:
        results: Resultados de las consultas en lote
    """
    st.subheader("📦 Resultados del Lote")
    
    # Estadísticas del lote
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Consultas", results.get('total_queries', 0))
    
    with col2:
        st.metric("Exitosas", results.get('successful_queries', 0))
    
    with col3:
        st.metric("Fallidas", results.get('failed_queries', 0))
    
    # Resultados individuales
    batch_results = results.get('results', [])
    for i, result in enumerate(batch_results):
        with st.expander(f"Consulta {i+1}: {result.get('query', 'N/A')[:50]}..."):
            st.write(f"**Respuesta:** {result.get('response', 'N/A')}")
            st.write(f"**Resultados encontrados:** {result.get('search_results_count', 0)}")
            st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")

def show_success_message(message: str):
    """Mostrar mensaje de éxito."""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message: str):
    """Mostrar mensaje de error."""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True) 