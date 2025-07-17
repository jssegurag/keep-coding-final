#!/usr/bin/env python3
"""
Script para probar las consultas en lote del sistema RAG Legal.
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_batch_queries():
    """Probar consultas en lote."""
    print("🚀 Probando consultas en lote del sistema RAG Legal")
    print("=" * 60)
    
    # URL de la API
    base_url = "http://localhost:8001"
    batch_endpoint = f"{base_url}/api/v1/queries/batch"
    
    # Datos de prueba
    test_queries = [
        "¿Cuál es el demandante del expediente RCCI2150725385?",
        "¿Qué fecha tiene el expediente RCCI2150725385?",
        "¿Cuál es el monto del expediente RCCI2150725385?",
        "¿Quién es el demandado del expediente RCCI2150725385?",
        "Dame un resumen del expediente RCCI2150725385"
    ]
    
    # Preparar datos para la petición
    batch_data = {
        "queries": [
            {"query": query, "n_results": 5} for query in test_queries
        ]
    }
    
    print("📋 Consultas a procesar:")
    for i, query in enumerate(test_queries, 1):
        print(f"   {i}. {query}")
    
    print(f"\n📤 Enviando petición a: {batch_endpoint}")
    print(f"📦 Datos enviados: {json.dumps(batch_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Realizar petición
        response = requests.post(
            batch_endpoint,
            json=batch_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Respuesta recibida:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Consultas en lote procesadas exitosamente!")
            print(f"📊 Estadísticas:")
            print(f"   • Total consultas: {result.get('total_queries', 0)}")
            print(f"   • Exitosas: {result.get('successful_queries', 0)}")
            print(f"   • Fallidas: {result.get('failed_queries', 0)}")
            print(f"   • Tiempo de procesamiento: {result.get('processing_time', 0):.2f}s")
            
            print(f"\n📋 Resultados individuales:")
            for i, result_item in enumerate(result.get('results', []), 1):
                print(f"\n   {i}. Consulta: {result_item.get('query', 'N/A')}")
                print(f"      Respuesta: {result_item.get('response', 'N/A')[:100]}...")
                print(f"      Resultados encontrados: {result_item.get('search_results_count', 0)}")
                print(f"      Estrategia: {result_item.get('search_strategy', 'N/A')}")
                
        else:
            print(f"\n❌ Error en la petición:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Intentar parsear el error
            try:
                error_data = response.json()
                print(f"   Error detallado: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Error raw: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Error de conexión: No se pudo conectar con la API en {base_url}")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload")
        
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout: La API no respondió en el tiempo esperado")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

def test_single_query_for_comparison():
    """Probar una consulta individual para comparar."""
    print("\n" + "=" * 60)
    print("🔍 Probando consulta individual para comparación")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    single_endpoint = f"{base_url}/api/v1/queries"
    
    single_data = {
        "query": "¿Cuál es el demandante del expediente RCCI2150725385?",
        "n_results": 5
    }
    
    print(f"📤 Enviando consulta individual a: {single_endpoint}")
    print(f"📦 Datos: {json.dumps(single_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            single_endpoint,
            json=single_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Respuesta individual:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Consulta individual exitosa!")
            print(f"   Respuesta: {result.get('response', 'N/A')[:100]}...")
            print(f"   Resultados: {result.get('search_results_count', 0)}")
            print(f"   Estrategia: {result.get('search_strategy', 'N/A')}")
        else:
            print(f"❌ Error en consulta individual: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en consulta individual: {str(e)}")

def main():
    """Función principal."""
    print("🧪 Test de Consultas en Lote - Sistema RAG Legal")
    print("=" * 60)
    
    # Probar consulta individual primero
    test_single_query_for_comparison()
    
    # Probar consultas en lote
    test_batch_queries()
    
    print("\n" + "=" * 60)
    print("🏁 Test completado")

if __name__ == "__main__":
    main() 