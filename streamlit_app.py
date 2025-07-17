#!/usr/bin/env python3
"""
Aplicación principal de Streamlit para el sistema RAG Legal.

Este archivo es el punto de entrada para ejecutar la interfaz de usuario
Streamlit del sistema RAG Legal, diseñado específicamente para abogados
que procesan oficios jurídicos en Colombia.

Para ejecutar la aplicación:
    streamlit run streamlit_app.py

Para ejecutar en modo desarrollo:
    streamlit run streamlit_app.py --server.port 8501 --server.address localhost
"""

import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.interface.app import run_app

if __name__ == "__main__":
    run_app() 