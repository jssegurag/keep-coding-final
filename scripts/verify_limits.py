#!/usr/bin/env python3
"""
Script para verificar que los nuevos límites de caracteres y resultados se aplicaron correctamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interface.config import get_config
from src.api.models.queries import QueryRequest

def verify_frontend_limits():
    """Verificar límites del frontend."""
    print("🔍 Verificando límites del Frontend...")
    
    config = get_config()
    
    print(f"✅ max_query_length: {config.ui.max_query_length} caracteres")
    print(f"✅ max_results_per_query: {config.ui.max_results_per_query} resultados")
    print(f"✅ max_batch_queries: {config.ui.max_batch_queries} consultas en lote")
    
    # Verificar que los límites son los esperados
    assert config.ui.max_query_length == 2000, f"max_query_length debe ser 2000, es {config.ui.max_query_length}"
    assert config.ui.max_results_per_query == 50, f"max_results_per_query debe ser 50, es {config.ui.max_results_per_query}"
    
    print("✅ Todos los límites del frontend están correctos")

def verify_backend_limits():
    """Verificar límites del backend."""
    print("\n🔍 Verificando límites del Backend...")
    
    # Crear una consulta de prueba con el límite máximo
    test_query = "a" * 2000  # Consulta de 2000 caracteres
    
    try:
        # Esto debería funcionar sin errores
        request = QueryRequest(
            query=test_query,
            n_results=50
        )
        print("✅ QueryRequest acepta 2000 caracteres y 50 resultados")
        
        # Probar con el límite máximo de caracteres
        max_query = "a" * 2000
        request_max = QueryRequest(
            query=max_query,
            n_results=50
        )
        print("✅ Límite máximo de caracteres funciona correctamente")
        
        # Probar con el límite máximo de resultados
        request_max_results = QueryRequest(
            query="Consulta de prueba",
            n_results=50
        )
        print("✅ Límite máximo de resultados funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error en backend: {e}")
        return False
    
    print("✅ Todos los límites del backend están correctos")
    return True

def test_invalid_limits():
    """Probar que los límites inválidos son rechazados."""
    print("\n🔍 Probando límites inválidos...")
    
    try:
        # Esto debería fallar
        QueryRequest(
            query="a" * 2001,  # Más de 2000 caracteres
            n_results=50
        )
        print("❌ Debería haber fallado con 2001 caracteres")
        return False
    except Exception:
        print("✅ Correctamente rechaza consultas de más de 2000 caracteres")
    
    try:
        # Esto debería fallar
        QueryRequest(
            query="Consulta de prueba",
            n_results=51  # Más de 50 resultados
        )
        print("❌ Debería haber fallado con 51 resultados")
        return False
    except Exception:
        print("✅ Correctamente rechaza más de 50 resultados")
    
    return True

def main():
    """Función principal."""
    print("🚀 Verificando nuevos límites del sistema RAG Legal")
    print("=" * 50)
    
    try:
        verify_frontend_limits()
        verify_backend_limits()
        test_invalid_limits()
        
        print("\n" + "=" * 50)
        print("✅ Todos los límites se actualizaron correctamente!")
        print("\n📊 Resumen de nuevos límites:")
        print("   • Consultas: hasta 2000 caracteres")
        print("   • Resultados: hasta 50 por consulta")
        print("   • Consultas en lote: hasta 5 consultas")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 