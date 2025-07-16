#!/usr/bin/env python3
"""
Script para verificar la indexación
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer

def main():
    print("Verificando indexación...")
    
    # Crear indexador
    indexer = ChromaIndexer()
    
    # Obtener estadísticas
    stats = indexer.get_collection_stats()
    
    if 'error' in stats:
        print(f"Error obteniendo estadísticas: {stats['error']}")
        return
    
    print(f"Estadísticas de la colección:")
    print(f"   - Chunks totales: {stats['total_chunks']}")
    print(f"   - Colección: {stats['collection_name']}")
    print(f"   - Metadatos disponibles: {', '.join(stats['sample_metadata_keys'])}")
    
    # Probar búsquedas
    test_queries = [
        "demandante",
        "embargo",
        "medida cautelar",
        "Juan Pérez"
    ]
    
    print(f"\nProbando búsquedas:")
    for query in test_queries:
        results = indexer.search_similar(query, n_results=3)
        
        if 'error' in results:
            print(f"   '{query}': {results['error']}")
        else:
            print(f"   '{query}': {results['total_found']} resultados")
    
    print("\nVerificación completada")

if __name__ == "__main__":
    main() 