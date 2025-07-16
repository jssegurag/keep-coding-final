#!/usr/bin/env python3
"""
Script para evaluar consultas con preguntas de prueba
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.query.query_handler import QueryHandler

def main():
    print("📊 Evaluación del Sistema de Consultas")
    print("=" * 50)
    
    # Consultas de prueba
    test_queries = [
        "¿Cuál es el demandante del expediente?",
        "¿Qué tipo de medida se solicitó?",
        "¿Cuál es la cuantía del embargo?",
        "¿En qué fecha se dictó la medida?",
        "¿Cuáles son los hechos principales del caso?",
        "¿Qué fundamentos jurídicos se esgrimen?",
        "¿Cuáles son las medidas cautelares solicitadas?",
        "Resume el expediente",
        "¿Cuál es el estado actual del proceso?",
        "¿Quién es el juez del caso?"
    ]
    
    # Inicializar query handler
    query_handler = QueryHandler()
    
    results = []
    
    print(f"🧪 Evaluando {len(test_queries)} consultas...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Procesando: {query}")
        
        try:
            result = query_handler.handle_query(query)
            
            # Evaluar calidad de respuesta
            quality_score = evaluate_response_quality(result['response'])
            
            result['quality_score'] = quality_score
            results.append(result)
            
            print(f"   ✅ Completado - Calidad: {quality_score}/5")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'query': query,
                'error': str(e),
                'quality_score': 0
            })
    
    # Calcular estadísticas
    successful = len([r for r in results if 'error' not in r])
    avg_quality = sum(r['quality_score'] for r in results) / len(results)
    
    print(f"\n📊 Resultados de Evaluación:")
    print(f"   - Consultas exitosas: {successful}/{len(test_queries)}")
    print(f"   - Calidad promedio: {avg_quality:.2f}/5")
    print(f"   - Tasa de éxito: {(successful/len(test_queries))*100:.1f}%")
    
    # Guardar resultados
    with open("logs/query_evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en logs/query_evaluation_results.json")

def evaluate_response_quality(response: str) -> int:
    """Evaluar calidad de respuesta (1-5)"""
    if not response or "Error" in response:
        return 1
    
    # Criterios de calidad
    score = 0
    
    # Respuesta no vacía
    if len(response) > 10:
        score += 1
    
    # Incluye información específica
    if any(keyword in response.lower() for keyword in ['demandante', 'demandado', 'embargo', 'medida']):
        score += 1
    
    # Incluye fuente
    if 'Fuente:' in response:
        score += 1
    
    # Respuesta coherente
    if not response.startswith("No se encuentra"):
        score += 1
    
    # Respuesta completa
    if len(response) > 50:
        score += 1
    
    return score

if __name__ == "__main__":
    main() 