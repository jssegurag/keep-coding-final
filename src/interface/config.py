"""
Configuración para la interfaz de usuario Streamlit del sistema RAG Legal.

Este módulo contiene todas las configuraciones necesarias para la interfaz
de usuario, incluyendo endpoints de la API, estilos, y configuraciones
específicas para abogados que procesan oficios jurídicos.
"""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class APIConfig:
    """Configuración de la API REST."""
    base_url: str = "http://localhost:8001"
    queries_endpoint: str = "/api/v1/queries"
    metadata_endpoint: str = "/api/v1/metadata"
    system_endpoint: str = "/api/v1/system"
    timeout: int = 30

@dataclass
class UIConfig:
    """Configuración de la interfaz de usuario."""
    page_title: str = "🏛️ Sistema RAG Legal - Procesamiento de Oficios Jurídicos"
    page_icon: str = "⚖️"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    # Configuraciones específicas para abogados
    max_query_length: int = 500
    max_results_per_query: int = 10
    max_batch_queries: int = 5
    
    # Configuraciones de paginación
    default_page_size: int = 10
    max_page_size: int = 50

@dataclass
class StyleConfig:
    """Configuración de estilos y temas."""
    primary_color: str = "#1f77b4"
    secondary_color: str = "#ff7f0e"
    success_color: str = "#2ca02c"
    warning_color: str = "#d62728"
    info_color: str = "#17a2b8"
    
    # Colores específicos para documentos legales
    sentencia_color: str = "#2E8B57"  # Verde mar
    demanda_color: str = "#DC143C"    # Carmesí
    recurso_color: str = "#FF8C00"    # Naranja oscuro
    auto_color: str = "#4169E1"       # Azul real
    acuerdo_color: str = "#32CD32"    # Verde lima

@dataclass
class AppConfig:
    """Configuración principal de la aplicación."""
    api: APIConfig = APIConfig()
    ui: UIConfig = UIConfig()
    style: StyleConfig = StyleConfig()
    
    # Configuraciones específicas para el dominio legal
    document_types: Dict[str, str] = None
    court_types: Dict[str, str] = None
    legal_entities: Dict[str, str] = None
    
    def __post_init__(self):
        """Inicializar configuraciones específicas del dominio legal."""
        if self.document_types is None:
            self.document_types = {
                "Sentencia": "Decisiones judiciales finales",
                "Demanda": "Documentos de inicio de proceso",
                "Recurso": "Apelaciones y recursos",
                "Auto": "Decisiones interlocutorias",
                "Acuerdo": "Acuerdos entre partes",
                "Oficio": "Comunicaciones oficiales",
                "Resolución": "Decisiones administrativas"
            }
        
        if self.court_types is None:
            self.court_types = {
                "Juzgado Civil": "Procesos civiles",
                "Juzgado Penal": "Procesos penales",
                "Juzgado Mercantil": "Procesos mercantiles",
                "Juzgado Laboral": "Procesos laborales",
                "Juzgado Familiar": "Procesos familiares",
                "Juzgado Administrativo": "Procesos administrativos",
                "Tribunal Superior": "Tribunales superiores",
                "Corte Suprema": "Corte suprema de justicia"
            }
        
        if self.legal_entities is None:
            self.legal_entities = {
                "demandante": "Persona que inicia el proceso",
                "demandado": "Persona contra quien se dirige la demanda",
                "abogado": "Representante legal",
                "procurador": "Representante del estado",
                "testigo": "Persona que declara",
                "perito": "Experto que emite concepto",
                "juez": "Funcionario que decide"
            }

# Instancia global de configuración
config = AppConfig()

def get_config() -> AppConfig:
    """Obtener la configuración global de la aplicación."""
    return config

def update_api_config(base_url: str = None, timeout: int = None):
    """Actualizar configuración de la API."""
    if base_url:
        config.api.base_url = base_url
    if timeout:
        config.api.timeout = timeout

def get_api_url(endpoint: str) -> str:
    """Construir URL completa para un endpoint de la API."""
    return f"{config.api.base_url}{endpoint}" 