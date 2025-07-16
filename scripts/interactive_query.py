#!/usr/bin/env python3
"""
Script interactivo para probar consultas
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.query.query_handler import QueryHandler
from src.query.filter_extractor import FilterExtractor

def main():
    print("🤖 Sistema de Consultas RAG - Modo Interactivo")
    print("=" * 50)
    print("Escribe 'salir' para terminar")
    print("Escribe 'ayuda' para ver ejemplos de consultas")
    print()
    
    # Inicializar componentes
    query_handler = QueryHandler()
    filter_extractor = FilterExtractor()
    
    # Ejemplos de consultas
    examples = [
        "¿Cuál es el demandante del expediente?",
        "¿Qué tipo de medida se solicitó?",
        "¿Cuál es la cuantía del embargo?",
        "Resume el expediente RCCI2150725310",
        "¿Cuáles son los hechos principales?",
        "embargos de Nury Romero"
    ]
    
    while True:
        try:
            # Obtener consulta del usuario
            query = input("\n🔍 Tu consulta: ").strip()
            
            if query.lower() == 'salir':
                print("👋 ¡Hasta luego!")
                break
            
            if query.lower() == 'ayuda':
                print("\n📝 Ejemplos de consultas:")
                for i, example in enumerate(examples, 1):
                    print(f"   {i}. {example}")
                continue
            
            if not query:
                print("❌ Por favor, ingresa una consulta válida")
                continue
            
            print(f"\n🔄 Procesando: {query}")
            
            # Extraer filtros (para debug)
            filters = filter_extractor.extract_filters(query)
            validated_filters = filter_extractor.validate_filters(filters)
            
            if validated_filters:
                print(f"🔍 Filtros detectados: {validated_filters}")
            
            # Procesar consulta
            result = query_handler.handle_query(query)
            
            # Mostrar respuesta
            print(f"\n💬 Respuesta:")
            print("-" * 40)
            print(result['response'])
            print("-" * 40)
            
            # Mostrar información adicional
            print(f"\n📊 Información:")
            print(f"   - Resultados encontrados: {result['search_results_count']}")
            print(f"   - Fuente: {result['source_info']['document_id']}")
            print(f"   - Chunk: {result['source_info']['chunk_position']}/{result['source_info']['total_chunks']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 