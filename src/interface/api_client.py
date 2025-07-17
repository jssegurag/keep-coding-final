"""
Cliente de API para comunicarse con el backend FastAPI del sistema RAG Legal.

Este módulo proporciona una interfaz limpia para realizar llamadas a la API REST,
manejando errores, timeouts y proporcionando respuestas estructuradas para
la interfaz de usuario Streamlit.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st
from .config import get_config, get_api_url

class APIClient:
    """Cliente para comunicarse con la API REST del sistema RAG Legal."""
    
    def __init__(self):
        """Inicializar cliente de API."""
        self.config = get_config()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Realizar petición HTTP a la API.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            data: Datos para enviar en el body
            params: Parámetros de query string
            
        Returns:
            Respuesta de la API como diccionario
            
        Raises:
            Exception: Si hay error en la comunicación con la API
        """
        url = get_api_url(endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.api.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("Timeout: La API no respondió en el tiempo esperado")
        except requests.exceptions.ConnectionError:
            raise Exception("Error de conexión: No se pudo conectar con la API")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception("Recurso no encontrado")
            elif e.response.status_code == 422:
                raise Exception("Datos de entrada inválidos")
            else:
                raise Exception(f"Error HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Error inesperado: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verificar el estado de salud del sistema.
        
        Returns:
            Información del estado del sistema
        """
        return self._make_request("GET", self.config.api.system_endpoint + "/health")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Obtener información general del sistema.
        
        Returns:
            Información del sistema
        """
        return self._make_request("GET", self.config.api.system_endpoint + "/info")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del sistema.
        
        Returns:
            Estadísticas del sistema
        """
        return self._make_request("GET", self.config.api.system_endpoint + "/stats")
    
    def perform_query(
        self, 
        query: str, 
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Realizar consulta semántica en documentos legales.
        
        Args:
            query: Consulta en lenguaje natural
            n_results: Número de resultados a retornar
            
        Returns:
            Respuesta de la consulta con información enriquecida
        """
        data = {
            "query": query,
            "n_results": min(n_results, self.config.ui.max_results_per_query)
        }
        
        return self._make_request("POST", self.config.api.queries_endpoint, data=data)
    
    def get_query_history(
        self, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Obtener historial de consultas realizadas.
        
        Args:
            page: Número de página
            page_size: Tamaño de página
            
        Returns:
            Historial de consultas paginado
        """
        params = {
            "page": page,
            "page_size": min(page_size, self.config.ui.max_page_size)
        }
        
        return self._make_request("GET", self.config.api.queries_endpoint + "/history", params=params)
    
    def perform_batch_queries(
        self, 
        queries: List[str]
    ) -> Dict[str, Any]:
        """
        Realizar múltiples consultas en lote.
        
        Args:
            queries: Lista de consultas a realizar
            
        Returns:
            Resultados de todas las consultas en lote
        """
        if len(queries) > self.config.ui.max_batch_queries:
            raise Exception(f"Máximo {self.config.ui.max_batch_queries} consultas por lote")
        
        data = {
            "queries": queries
        }
        
        return self._make_request("POST", self.config.api.queries_endpoint + "/batch", data=data)
    
    def get_documents_metadata(
        self,
        page: int = 1,
        page_size: int = 10,
        document_type: Optional[str] = None,
        court: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtener metadatos de documentos con filtros.
        
        Args:
            page: Número de página
            page_size: Tamaño de página
            document_type: Filtro por tipo de documento
            court: Filtro por tribunal
            
        Returns:
            Metadatos de documentos paginados
        """
        # Este endpoint requiere datos CSV que pueden no estar disponibles
        # Retornar respuesta vacía si no hay datos
        return {
            "documents": [],
            "total_count": 0,
            "available_filters": {}
        }
    
    def get_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """
        Obtener metadatos de un documento específico.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Metadatos del documento
        """
        # Este endpoint requiere datos CSV que pueden no estar disponibles
        raise Exception("Funcionalidad no disponible en esta versión")
    
    def get_document_summary(self, document_id: str) -> Dict[str, Any]:
        """
        Obtener resumen ejecutivo de un documento.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Resumen del documento
        """
        # Este endpoint requiere datos CSV que pueden no estar disponibles
        raise Exception("Funcionalidad no disponible en esta versión")

def get_api_client() -> APIClient:
    """Obtener instancia del cliente de API."""
    return APIClient()

def test_api_connection() -> bool:
    """
    Probar la conexión con la API.
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        client = get_api_client()
        client.health_check()
        return True
    except Exception as e:
        st.error(f"Error de conexión con la API: {str(e)}")
        return False 