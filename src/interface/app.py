"""
Aplicación principal de Streamlit para el sistema RAG Legal.

Este módulo contiene la aplicación principal que orquesta todas las páginas
y funcionalidades del sistema, diseñado específicamente para abogados
que procesan oficios jurídicos en Colombia.
"""

import streamlit as st
from typing import Dict, Any
from .components import render_header, render_sidebar
from .pages import (
    render_home_page,
    render_queries_page,
    render_documents_page,
    render_history_page,
    render_system_page
)
from .api_client import test_api_connection

def initialize_session_state():
    """Inicializar variables de estado de la sesión."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'refresh_documents' not in st.session_state:
        st.session_state.refresh_documents = False
    if 'api_connection_tested' not in st.session_state:
        st.session_state.api_connection_tested = False

def main():
    """Función principal de la aplicación Streamlit."""
    
    # Inicializar estado de la sesión
    initialize_session_state()
    
    # Renderizar encabezado y configuración
    render_header()
    
    # Renderizar barra lateral y obtener página seleccionada
    selected_page = render_sidebar()
    
    # Verificar conexión con la API (solo una vez por sesión)
    if not st.session_state.api_connection_tested:
        st.session_state.api_connection_tested = True
        if not test_api_connection():
            st.error("""
            ⚠️ **Error de Conexión con la API**
            
            No se pudo conectar con el servidor de la API. Por favor:
            
            1. **Verifique que el servidor FastAPI esté ejecutándose**
            2. **Confirme que la URL de la API sea correcta**
            3. **Revise los logs del servidor para errores**
            
            Para iniciar el servidor, ejecute:
            ```bash
            uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
            ```
            """)
            return
    
    # Renderizar página seleccionada
    try:
        if selected_page == "🏠 Inicio":
            render_home_page()
        elif selected_page == "🔍 Consultas Semánticas":
            render_queries_page()
        elif selected_page == "📊 Historial de Consultas":
            render_history_page()
        elif selected_page == "⚙️ Configuración del Sistema":
            render_system_page()
        else:
            st.error(f"Página no encontrada: {selected_page}")
            
    except Exception as e:
        st.error(f"""
        ❌ **Error en la aplicación**
        
        Se produjo un error inesperado: {str(e)}
        
        Por favor:
        1. **Recargue la página**
        2. **Verifique la conexión con la API**
        3. **Contacte al equipo de desarrollo si el problema persiste**
        """)
        
        # Mostrar información de debug en modo desarrollo
        if st.checkbox("Mostrar información de debug"):
            st.exception(e)

def run_app():
    """Ejecutar la aplicación Streamlit."""
    try:
        main()
    except Exception as e:
        st.error(f"Error crítico en la aplicación: {str(e)}")
        st.stop()

if __name__ == "__main__":
    run_app() 