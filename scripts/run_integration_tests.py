#!/usr/bin/env python3
"""
Script para ejecutar tests de integración
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.testing.integration_tester import IntegrationTester

def main():
    print("🧪 Ejecutando Tests de Integración")
    print("=" * 50)
    
    # Crear tester
    tester = IntegrationTester()
    
    # Mostrar información sobre datos reales
    real_data = tester.real_data
    print(f"📊 Datos reales disponibles:")
    print(f"   - Documentos totales: {real_data.get('total_available', 0)}")
    print(f"   - Documentos para testing: {len(real_data.get('documents', []))}")
    
    if real_data.get('documents'):
        print(f"   - Expedientes de ejemplo:")
        for i, doc in enumerate(real_data['documents'][:3]):
            demandante = doc.get('demandante', {})
            nombres = demandante.get('nombresPersonaDemandante', '')
            apellidos = demandante.get('apellidosPersonaDemandante', '')
            empresa = demandante.get('NombreEmpresaDemandante', '')
            
            if nombres and apellidos:
                print(f"     {i+1}. {doc['document_id']} - {nombres} {apellidos}")
            elif empresa:
                print(f"     {i+1}. {doc['document_id']} - {empresa}")
    
    # Ejecutar test end-to-end
    print(f"\n1️⃣ Test End-to-End del Pipeline")
    e2e_results = tester.test_end_to_end_pipeline()
    
    # Mostrar resultados
    print(f"\n📊 Resultados End-to-End:")
    
    # Componentes individuales
    components = e2e_results.get("components", {})
    print(f"   - Chunker: {'✅' if components.get('chunker', {}).get('success') else '❌'}")
    print(f"   - Indexer: {'✅' if components.get('indexer', {}).get('success') else '❌'}")
    print(f"   - Query Handler: {'✅' if components.get('query_handler', {}).get('success') else '❌'}")
    
    # Indexación
    indexing = e2e_results.get("indexing", {})
    if indexing.get("success"):
        print(f"   - Indexación: ✅ ({indexing.get('total_chunks', 0)} chunks)")
    else:
        print(f"   - Indexación: ❌")
    
    # Búsqueda
    search = e2e_results.get("search", {})
    if search.get("success"):
        print(f"   - Búsqueda: ✅")
    else:
        print(f"   - Búsqueda: ❌")
    
    # Consultas
    queries = e2e_results.get("queries", {})
    if queries.get("success"):
        print(f"   - Consultas: ✅")
    else:
        print(f"   - Consultas: ❌")
    
    # Pipeline completo
    pipeline = e2e_results.get("pipeline", {})
    if pipeline.get("success"):
        print(f"   - Pipeline Completo: ✅ ({pipeline.get('response_time', 0):.2f}s)")
    else:
        print(f"   - Pipeline Completo: ❌")
    
    # Ejecutar evaluación cualitativa
    print(f"\n2️⃣ Evaluación Cualitativa")
    evaluation_results = tester.run_qualitative_evaluation()
    
    summary = evaluation_results.get("summary", {})
    print(f"\n📊 Resultados de Evaluación:")
    print(f"   - Preguntas exitosas: {summary.get('successful_questions', 0)}/20")
    print(f"   - Tasa de éxito: {summary.get('success_rate', 0):.1f}%")
    print(f"   - Calidad promedio: {summary.get('average_quality', 0):.2f}/5")
    print(f"   - Tiempo promedio: {summary.get('average_response_time', 0):.2f}s")
    print(f"   - Con fuente: {summary.get('questions_with_source', 0)}/20")
    print(f"   - Documentos reales probados: {summary.get('real_documents_tested', 0)}")
    
    # Distribución de calidad
    quality_dist = summary.get("quality_distribution", {})
    print(f"\n📈 Distribución de Calidad:")
    print(f"   - Excelente (4-5): {quality_dist.get('excellent', 0)}")
    print(f"   - Buena (3-4): {quality_dist.get('good', 0)}")
    print(f"   - Aceptable (2-3): {quality_dist.get('acceptable', 0)}")
    print(f"   - Pobre (1-2): {quality_dist.get('poor', 0)}")
    
    # Mostrar ejemplos de preguntas con documentos reales
    questions = evaluation_results.get("questions", [])
    real_questions = [q for q in questions if q.get("real_document")]
    
    if real_questions:
        print(f"\n📋 Ejemplos de preguntas con documentos reales:")
        for q in real_questions[:3]:
            print(f"   - {q['question']} (Calidad: {q['quality_score']}/5)")
    
    # Guardar resultados
    all_results = {
        "end_to_end": e2e_results,
        "qualitative_evaluation": evaluation_results,
        "real_data_info": {
            "total_available": real_data.get("total_available", 0),
            "documents_used": len(real_data.get("documents", [])),
            "real_documents_tested": summary.get("real_documents_tested", 0)
        }
    }
    
    with open("logs/integration_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en logs/integration_test_results.json")
    
    # Evaluación final
    success_rate = summary.get("success_rate", 0)
    avg_quality = summary.get("average_quality", 0)
    real_docs_tested = summary.get("real_documents_tested", 0)
    
    if success_rate >= 80 and avg_quality >= 3.5 and real_docs_tested >= 5:
        print(f"\n🎉 ¡MVP VALIDADO! Sistema listo para producción")
        print(f"   ✅ Tasa de éxito: {success_rate:.1f}%")
        print(f"   ✅ Calidad promedio: {avg_quality:.2f}/5")
        print(f"   ✅ Documentos reales probados: {real_docs_tested}")
    elif success_rate >= 60 and avg_quality >= 3.0:
        print(f"\n⚠️ MVP ACEPTABLE - Considerar optimizaciones")
        print(f"   ⚠️ Tasa de éxito: {success_rate:.1f}%")
        print(f"   ⚠️ Calidad promedio: {avg_quality:.2f}/5")
        print(f"   ⚠️ Documentos reales probados: {real_docs_tested}")
    else:
        print(f"\n❌ MVP NO CUMPLE CRITERIOS - Requiere mejoras")
        print(f"   ❌ Tasa de éxito: {success_rate:.1f}%")
        print(f"   ❌ Calidad promedio: {avg_quality:.2f}/5")
        print(f"   ❌ Documentos reales probados: {real_docs_tested}")

if __name__ == "__main__":
    main() 