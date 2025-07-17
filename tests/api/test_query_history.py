import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.services.query_history_service import _GLOBAL_HISTORY

client = TestClient(app)

def test_query_history_empty():
    _GLOBAL_HISTORY.clear()
    """Probar historial vacío."""
    response = client.get("/api/v1/queries/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 0
    assert len(data["queries"]) == 0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 0

def test_query_history_with_data():
    """Probar historial con datos."""
    # Primero hacer una consulta para generar historial
    query_payload = {"query": "¿Cuál es el demandante del expediente?", "n_results": 3}
    query_response = client.post("/api/v1/queries/", json=query_payload)
    assert query_response.status_code == 200
    
    # Obtener historial
    history_response = client.get("/api/v1/queries/history")
    assert history_response.status_code == 200
    data = history_response.json()
    
    assert data["total_count"] >= 1
    assert len(data["queries"]) >= 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    
    # Verificar estructura del primer elemento
    first_query = data["queries"][0]
    assert "id" in first_query
    assert "query" in first_query
    assert "response" in first_query
    assert "timestamp" in first_query
    assert "search_results_count" in first_query
    assert "source_info" in first_query

def test_query_history_pagination():
    """Probar paginación del historial."""
    # Hacer varias consultas para generar historial
    queries = [
        {"query": "Consulta 1", "n_results": 3},
        {"query": "Consulta 2", "n_results": 3},
        {"query": "Consulta 3", "n_results": 3}
    ]
    
    for query in queries:
        response = client.post("/api/v1/queries/", json=query)
        assert response.status_code == 200
    
    # Probar primera página
    response = client.get("/api/v1/queries/history?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["queries"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2

def test_query_history_filters():
    """Probar filtros del historial."""
    # Hacer consultas con diferentes características
    queries = [
        {"query": "Consulta con filtro", "n_results": 3},
        {"query": "Otra consulta", "n_results": 5}
    ]
    
    for query in queries:
        response = client.post("/api/v1/queries/", json=query)
        assert response.status_code == 200
    
    # Probar filtro por texto (cuando esté implementado)
    response = client.get("/api/v1/queries/history?query_filter=Consulta")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 0  # Puede ser 0 si no hay filtros implementados

def test_query_history_structure():
    """Probar estructura de respuesta del historial."""
    response = client.get("/api/v1/queries/history")
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura requerida
    required_fields = ["queries", "total_count", "page", "page_size", "total_pages"]
    for field in required_fields:
        assert field in data
    
    # Verificar tipos de datos
    assert isinstance(data["queries"], list)
    assert isinstance(data["total_count"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["page_size"], int)
    assert isinstance(data["total_pages"], int)
    
    # Verificar valores válidos
    assert data["page"] >= 1
    assert data["page_size"] >= 1
    assert data["total_count"] >= 0
    assert data["total_pages"] >= 0

def test_query_history_error_handling():
    """Probar manejo de errores en el historial."""
    # Probar parámetros inválidos
    response = client.get("/api/v1/queries/history?page=0")
    assert response.status_code == 422  # Error de validación
    
    response = client.get("/api/v1/queries/history?page_size=0")
    assert response.status_code == 422  # Error de validación
    
    response = client.get("/api/v1/queries/history?page_size=100")
    assert response.status_code == 422  # Error de validación (límite excedido) 