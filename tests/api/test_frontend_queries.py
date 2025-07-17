import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.testing.integration_tester import IntegrationTester

client = TestClient(app)
tester = IntegrationTester()

def validate_rag_response(data):
    assert "query" in data, "La respuesta debe contener la consulta original"
    assert "response" in data, "La respuesta debe contener el texto generado"
    assert "timestamp" in data, "La respuesta debe contener timestamp"
    
    # Verificar que la respuesta no esté vacía
    assert data["response"].strip(), "La respuesta no debe estar vacía"
    
    # Verificar que la respuesta no sea genérica
    generic_responses = [
        "No se encontraron documentos relevantes",
        "No se encuentra en el expediente proporcionado",
        "No hay información disponible"
    ]
    
    response_text = data["response"].lower()
    is_generic = any(generic in response_text for generic in generic_responses)
    
    # Si es genérica, verificar que al menos tenga información de fuente
    if is_generic:
        assert "fuente:" in response_text.lower() or "source:" in response_text.lower(), \
        "Respuesta genérica debe incluir información de fuente"
    else:
        # Para respuestas no genéricas, verificar que contengan información útil
        assert len(data["response"]) > 50, "La respuesta debe tener contenido sustancial"
    
    # Verificar entidades extraídas
    assert "entities" in data, "La respuesta debe contener entidades extraídas"
    entities = data["entities"]
    assert isinstance(entities, dict), "Entities debe ser un diccionario"
    
    # Verificar información de fuente
    assert "source_info" in data, "La respuesta debe contener información de fuente"
    source_info = data["source_info"]
    assert isinstance(source_info, dict), "Source_info debe ser un diccionario"
    
    # Verificar que search_results_count sea un número válido
    assert "search_results_count" in data, "La respuesta debe contener conteo de resultados"
    assert isinstance(data["search_results_count"], int), "search_results_count debe ser entero"
    assert data["search_results_count"] >= 0, "search_results_count debe ser >=0"

@pytest.mark.parametrize("question", [q["question"] for q in tester.evaluation_questions])
def test_frontend_query(question):
    payload = {"query": question, "n_results": 3}
    response = client.post("/api/v1/queries/", json=payload)
    
    # Verificar status code
    assert response.status_code == 200, f"El endpoint debe responder 200, obtuvo {response.status_code}"
    
    # Obtener datos de respuesta
    data = response.json()
    
    # Validar respuesta semánticamente
    validate_rag_response(data)
    
    # Verificar que la consulta original se mantenga
    assert data["query"] == question, "La consulta original debe mantenerse en la respuesta"
    
    # Verificar timestamp válido
    from datetime import datetime
    timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    assert timestamp.year >= 2024, "Timestamp debe ser válido"

def test_query_with_specific_document():
    payload = {"query": "¿Cuál es el demandante del expediente RCCI2150725372?", "n_results": 3}
    response = client.post("/api/v1/queries/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Validaciones específicas para esta consulta
    validate_rag_response(data)
    
    # Verificar que se extrajo el número de expediente
    entities = data["entities"]
    if "document_numbers" in entities:
        assert "RCCI2150725372" in entities["document_numbers"], \
          "Debe extraer el número de expediente de la consulta"
    
    # Verificar que se aplicó el filtro correcto
    if "filters_used" in data and data["filters_used"]:
        assert "document_id" in data["filters_used"], \
            "Debe aplicar filtro por document_id cuando se menciona un expediente específico"

def test_query_with_legal_terms():
    payload = {"query": "¿Cuál es la cuantía del embargo?", "n_results": 3}
    response = client.post("/api/v1/queries/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    validate_rag_response(data)
    
    # Verificar que se extrajeron términos legales
    entities = data["entities"]
    if "legal_terms" in entities:
        legal_terms = entities["legal_terms"]
        assert len(legal_terms) > 0, "Debe extraer términos legales de la consulta"
        assert any("embargo" in term.lower() for term in legal_terms), \
           "Debe reconocer 'embargo' como término legal" 