#!/usr/bin/env python3
"""
Script para validar embeddings con textos legales
Siguiendo principios SOLID y GRASP
"""
import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.testing.embedding_validator import EmbeddingValidator

def main():
    """
    Función principal del script de validación.
    Responsabilidad única: Orquestar el proceso de validación.
    """
    print("Iniciando validación de embeddings...")
    
    try:
        # Crear validador
        validator = EmbeddingValidator()
        
        # Ejecutar validación
        results = validator.run_validation()
        
        # Imprimir resultados
        validator.print_results(results)
        
        # Guardar resultados
        save_results(results)
        
        print("Validación completada. Resultados guardados en logs/embedding_validation_results.json")
        
    except Exception as e:
        print(f"Error durante la validación: {e}")
        sys.exit(1)

def save_results(results: dict):
    """
    Guardar resultados de validación en archivo JSON.
    Responsabilidad única: Persistencia de resultados.
    """
    try:
        # Crear directorio logs si no existe
        os.makedirs("logs", exist_ok=True)
        
        # Guardar resultados
        with open("logs/embedding_validation_results.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error guardando resultados: {e}")

if __name__ == "__main__":
    main() 