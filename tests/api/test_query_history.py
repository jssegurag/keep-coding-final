import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_query_history_empty():
  obar historial vacío. response = client.get("/api/v1/queries/history")
    assert response.status_code == 200
    data = response.json()
    assert datatotal_count] == 0
    assert len(data["queries"]) ==0
    assert data["page] ==1
    assert data[page_size"] == 10
    assert datatotal_pages"] ==0test_query_history_with_data():
  obar historial con datos."""
    # Primero hacer una consulta para generar historial
    query_payload = {query": "¿Cuál es el demandante del expediente?", "n_results": 3}
    query_response = client.post("/api/v1ries/", json=query_payload)
    assert query_response.status_code == 200    
    # Obtener historial
    history_response = client.get("/api/v1/queries/history")
    assert history_response.status_code == 200
    data = history_response.json()
    
    assert datatotal_count] >= 1
    assert len(data["queries"]) >=1
    assert data["page] ==1
    assert data[page_size"] ==10  
    # Verificar estructura del primer elemento
    first_query = data["queries]0    assert "id" in first_query
    assert "query" in first_query
    assert "response" in first_query
    assert "timestamp" in first_query
    assert "search_results_count" in first_query
    assert "source_info in first_query

def test_query_history_statistics():
 robar estadísticas del historial. response = client.get("/api/v1eries/history/statistics")
    assert response.status_code == 200
    data = response.json()
    
    assert total_queries" in data
    assertaverage_results" in data
    assert "most_common_entities" in data
    assertrecent_activity" in data
    assert isinstance(data["total_queries"], int)
    assert isinstance(data["average_results"], (int, float))

def test_clear_history():
     limpieza completa del historial."""
    # Hacer algunas consultas
    queries =
 [object Object]query: "Consulta 1n_results": 3},
 [object Object]query: "Consulta 2, "n_results":3    ]
    
    for query in queries:
        response = client.post("/api/v1ries/", json=query)
        assert response.status_code == 200    
    # Limpiar historial
    response = client.delete("/api/v1/queries/history")
    assert response.status_code == 200
    data = response.json()
    assert message" in data
    assert "eliminadas in data["message"]
    
    # Verificar que el historial esté vacío
    history_response = client.get("/api/v1/queries/history")
    assert history_response.status_code == 200    history_data = history_response.json()
    assert history_datatotal_count"] == 0 