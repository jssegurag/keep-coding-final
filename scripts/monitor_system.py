#!/usr/bin/env python3
"""
Script para monitoreo del sistema RAG
"""
import sys
import os
import json
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer
from src.query.query_handler import QueryHandler

def main():
    print("📊 Monitoreo del Sistema RAG")
    print("=" * 40)
    
    # Inicializar componentes
    indexer = ChromaIndexer()
    query_handler = QueryHandler()
    
    # Obtener estadísticas
    print("📈 Estadísticas del Sistema:")
    
    # Estadísticas de indexación
    stats = indexer.get_collection_stats()
    if "error" not in stats:
        print(f"   - Chunks indexados: {stats.get('total_chunks', 0)}")
        print(f"   - Colección: {stats.get('collection_name', 'N/A')}")
        print(f"   - Metadatos disponibles: {len(stats.get('sample_metadata_keys', []))}")
    else:
        print(f"   ❌ Error obteniendo estadísticas: {stats['error']}")
    
    # Probar consultas de monitoreo
    monitoring_queries = [
        "demandante",
        "embargo",
        "medida cautelar"
    ]
    
    print(f"\n🔍 Pruebas de Consulta:")
    for query in monitoring_queries:
        try:
            start_time = time.time()
            result = query_handler.handle_query(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if "error" not in result:
                print(f"   ✅ '{query}': {result['search_results_count']} resultados ({response_time:.2f}s)")
            else:
                print(f"   ❌ '{query}': Error")
                
        except Exception as e:
            print(f"   ❌ '{query}': {e}")
    
    # Verificar logs
    print(f"\n📋 Estado de Logs:")
    log_files = [
        "logs/chunking.log",
        "logs/indexing.log", 
        "logs/query.log",
        "logs/integration_testing.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"   ✅ {log_file}: {size} bytes")
        else:
            print(f"   ❌ {log_file}: No existe")
    
    print(f"\n✅ Monitoreo completado")

if __name__ == "__main__":
    main() 