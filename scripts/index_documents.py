#!/usr/bin/env python3
"""
Script para indexar documentos en ChromaDB
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer
from config.settings import CSV_METADATA_PATH, JSON_DOCS_PATH
import pandas as pd

def main():
    print("Iniciando indexación de documentos...")
    
    # Crear indexador
    indexer = ChromaIndexer()
    
    # Verificar archivos de entrada
    if not os.path.exists(CSV_METADATA_PATH):
        print(f"No se encontró el archivo CSV: {CSV_METADATA_PATH}")
        return
    
    if not os.path.exists(JSON_DOCS_PATH):
        print(f"No se encontró el directorio JSON: {JSON_DOCS_PATH}")
        return
    
    # Indexar documentos
    result = indexer.load_and_index_from_csv()
    
    if result.get('success', False):
        print(f"Indexación completada:")
        print(f"   - Documentos totales: {result['total_documents']}")
        print(f"   - Exitosos: {result['successful']}")
        print(f"   - Fallidos: {result['failed']}")
        print(f"   - Tasa de éxito: {result['success_rate']:.1f}%")
        
        # Mostrar estadísticas
        stats = indexer.get_collection_stats()
        print(f"\nEstadísticas de la colección:")
        print(f"   - Chunks totales: {stats['total_chunks']}")
        print(f"   - Nombre: {stats['collection_name']}")
        print(f"   - Metadatos disponibles: {', '.join(stats['sample_metadata_keys'])}")
        
    else:
        print(f"Error en indexación: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 