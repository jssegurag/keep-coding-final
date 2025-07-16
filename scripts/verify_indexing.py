#!/usr/bin/env python3
"""
Script para verificar la indexación completada y generar reportes de calidad.
Sigue los principios SOLID y GRASP para mantener la coherencia del sistema.
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from src.indexing.chroma_indexer import ChromaIndexer
from config.settings import CSV_METADATA_PATH, CHROMA_COLLECTION_NAME

def verify_indexing_completion() -> Dict[str, Any]:
    """
    Verifica el estado de la indexación completada.
    
    :return: Diccionario con resultados de verificación
    """
    print("🔍 Verificando estado de indexación...")
    
    try:
        # Inicializar indexador
        indexer = ChromaIndexer()
        
        # Obtener estadísticas de la colección
        stats = indexer.get_collection_stats()
        
        # Cargar CSV de metadatos
        df = pd.read_csv(CSV_METADATA_PATH)
        total_documents = len(df)
        
        # Verificar documentos indexados
        indexed_count = stats.get('total_chunks', 0)
        
        # Calcular métricas
        verification_results = {
            'timestamp': datetime.now().isoformat(),
            'collection_name': CHROMA_COLLECTION_NAME,
            'total_documents_csv': total_documents,
            'total_chunks_indexed': indexed_count,
            'indexing_complete': indexed_count > 0,
            'collection_stats': stats,
            'sample_metadata_keys': stats.get('sample_metadata_keys', []),
            'last_updated': stats.get('last_updated', '')
        }
        
        return verification_results
        
    except Exception as e:
        print(f"❌ Error verificando indexación: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'indexing_complete': False
        }

def test_search_functionality() -> Dict[str, Any]:
    """
    Prueba la funcionalidad de búsqueda para verificar calidad.
    
    :return: Diccionario con resultados de búsqueda
    """
    print("🔍 Probando funcionalidad de búsqueda...")
    
    try:
        indexer = ChromaIndexer()
        
        # Consultas de prueba
        test_queries = [
            "demandante",
            "resolución",
            "documento legal",
            "proceso judicial"
        ]
        
        search_results = {}
        
        for query in test_queries:
            result = indexer.search_similar(query, n_results=5)
            search_results[query] = {
                'total_found': result.get('total_found', 0),
                'has_results': result.get('total_found', 0) > 0,
                'query': query
            }
        
        return {
            'timestamp': datetime.now().isoformat(),
            'test_queries': test_queries,
            'search_results': search_results,
            'search_functional': any(r['has_results'] for r in search_results.values())
        }
        
    except Exception as e:
        print(f"❌ Error probando búsqueda: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'search_functional': False
        }

def generate_quality_report() -> Dict[str, Any]:
    """
    Genera un reporte completo de calidad de la indexación.
    
    :return: Diccionario con reporte de calidad
    """
    print("📊 Generando reporte de calidad...")
    
    # Verificar indexación
    indexing_verification = verify_indexing_completion()
    
    # Probar búsqueda
    search_verification = test_search_functionality()
    
    # Generar reporte completo
    quality_report = {
        'report_timestamp': datetime.now().isoformat(),
        'indexing_verification': indexing_verification,
        'search_verification': search_verification,
        'overall_status': {
            'indexing_complete': indexing_verification.get('indexing_complete', False),
            'search_functional': search_verification.get('search_functional', False),
            'system_ready': indexing_verification.get('indexing_complete', False) and 
                          search_verification.get('search_functional', False)
        },
        'recommendations': []
    }
    
    # Generar recomendaciones
    if not indexing_verification.get('indexing_complete', False):
        quality_report['recommendations'].append("Ejecutar pipeline completo para indexar documentos")
    
    if not search_verification.get('search_functional', False):
        quality_report['recommendations'].append("Verificar configuración de embeddings y ChromaDB")
    
    if indexing_verification.get('total_chunks_indexed', 0) == 0:
        quality_report['recommendations'].append("No se encontraron chunks indexados")
    
    return quality_report

def save_report(report: Dict[str, Any], output_path: str = "logs/indexing_verification_report.json"):
    """
    Guarda el reporte de verificación.
    
    :param report: Reporte a guardar
    :param output_path: Ruta de salida
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte guardado en: {output_path}")
        
    except Exception as e:
        print(f"❌ Error guardando reporte: {e}")

def print_summary(report: Dict[str, Any]):
    """
    Imprime un resumen del reporte de verificación.
    
    :param report: Reporte a resumir
    """
    print("\n" + "="*50)
    print("📊 RESUMEN DE VERIFICACIÓN DE INDEXACIÓN")
    print("="*50)
    
    # Estado general
    overall = report.get('overall_status', {})
    print(f"✅ Indexación Completada: {overall.get('indexing_complete', False)}")
    print(f"✅ Búsqueda Funcional: {overall.get('search_functional', False)}")
    print(f"✅ Sistema Listo: {overall.get('system_ready', False)}")
    
    # Estadísticas de indexación
    indexing = report.get('indexing_verification', {})
    print(f"\n📈 Estadísticas de Indexación:")
    print(f"   📄 Documentos en CSV: {indexing.get('total_documents_csv', 0)}")
    print(f"   🔍 Chunks Indexados: {indexing.get('total_chunks_indexed', 0)}")
    print(f"   📁 Colección: {indexing.get('collection_name', 'N/A')}")
    
    # Resultados de búsqueda
    search = report.get('search_verification', {})
    results = search.get('search_results', {})
    print(f"\n🔍 Pruebas de Búsqueda:")
    for query, result in results.items():
        status = "✅" if result.get('has_results', False) else "❌"
        print(f"   {status} '{query}': {result.get('total_found', 0)} resultados")
    
    # Recomendaciones
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recomendaciones:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print(f"\n🎉 ¡Sistema funcionando correctamente!")
    
    print("="*50)

def main():
    """
    Función principal que ejecuta la verificación completa.
    """
    print("🚀 Iniciando verificación de indexación...")
    
    try:
        # Generar reporte de calidad
        report = generate_quality_report()
        
        # Guardar reporte
        save_report(report)
        
        # Imprimir resumen
        print_summary(report)
        
        # Retornar código de salida
        if report.get('overall_status', {}).get('system_ready', False):
            print("\n✅ Verificación completada exitosamente")
            return 0
        else:
            print("\n⚠️ Verificación completada con advertencias")
            return 1
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 