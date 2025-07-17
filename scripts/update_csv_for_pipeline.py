#!/usr/bin/env python3
"""
Script para actualizar el CSV de metadatos para que apunte a los archivos JSON generados por el pipeline.
Sigue los principios SOLID y GRASP para mantener la coherencia del sistema.
"""

import os
import pandas as pd
import json
from typing import Dict, List, Optional
from pathlib import Path

def extract_document_id_from_path(file_path: str) -> Optional[str]:
    """
    Extrae el ID del documento desde la ruta del archivo.
    
    :param file_path: Ruta del archivo PDF
    :return: ID del documento (nombre del archivo sin extensión)
    """
    try:
        # Extraer el nombre del archivo de la ruta
        filename = os.path.basename(file_path)
        # Remover la extensión .pdf
        document_id = filename.replace('.pdf', '')
        return document_id
    except Exception as e:
        print(f"⚠️ Error extrayendo ID de documento de {file_path}: {e}")
        return None

def verify_json_exists(document_id: str, target_path: str = "target/") -> bool:
    """
    Verifica si existe el archivo JSON correspondiente al documento.
    
    :param document_id: ID del documento
    :param target_path: Ruta del directorio target
    :return: True si existe el archivo JSON
    """
    json_path = os.path.join(target_path, f"{document_id}.pdf", "output.json")
    return os.path.exists(json_path)

def update_csv_for_pipeline(csv_path: str, target_path: str = "target/") -> pd.DataFrame:
    """
    Actualiza el CSV para que apunte a los archivos JSON generados por el pipeline.
    
    :param csv_path: Ruta del CSV original
    :param target_path: Ruta del directorio target
    :return: DataFrame actualizado
    """
    print(f"🔍 Actualizando CSV: {csv_path}")
    print(f"📁 Directorio target: {target_path}")
    
    # Leer el CSV original
    df = pd.read_csv(csv_path)
    print(f"📊 Documentos en CSV: {len(df)}")
    
    # Crear nuevas columnas para el pipeline
    df['document_id'] = df['documentname'].apply(extract_document_id_from_path)
    df['json_path'] = df['document_id'].apply(
        lambda doc_id: f"{target_path}{doc_id}.pdf/output.json" if doc_id else None
    )
    df['json_exists'] = df['json_path'].apply(
        lambda path: os.path.exists(path) if path else False
    )
    
    # Filtrar solo documentos que existen en el pipeline
    pipeline_docs = df[df['json_exists'] == True].copy()
    print(f"✅ Documentos encontrados en pipeline: {len(pipeline_docs)}")
    
    # Crear CSV actualizado para el pipeline
    pipeline_csv = pipeline_docs[['id', 'document_id', 'json_path', 'response']].copy()
    pipeline_csv.columns = ['id', 'document_id', 'json_path', 'metadata']
    
    return pipeline_csv

def save_updated_csv(df: pd.DataFrame, output_path: str):
    """
    Guarda el CSV actualizado.
    
    :param df: DataFrame actualizado
    :param output_path: Ruta de salida
    """
    df.to_csv(output_path, index=False)
    print(f"💾 CSV actualizado guardado en: {output_path}")

def main():
    """
    Función principal que ejecuta la actualización del CSV.
    """
    csv_path = "src/resources/metadata/studio_results_20250715_2237.csv"
    target_path = "target/"
    output_path = "src/resources/metadata/pipeline_metadata.csv"
    
    try:
        # Verificar que existe el CSV original
        if not os.path.exists(csv_path):
            print(f"❌ CSV original no encontrado: {csv_path}")
            return
        
        # Verificar que existe el directorio target
        if not os.path.exists(target_path):
            print(f"❌ Directorio target no encontrado: {target_path}")
            return
        
        # Actualizar CSV
        updated_df = update_csv_for_pipeline(csv_path, target_path)
        
        if len(updated_df) == 0:
            print("⚠️ No se encontraron documentos procesados por el pipeline")
            return
        
        # Guardar CSV actualizado
        save_updated_csv(updated_df, output_path)
        
        # Mostrar estadísticas
        print("\n📊 Estadísticas:")
        print(f"   📄 Total documentos en CSV original: {len(pd.read_csv(csv_path))}")
        print(f"   ✅ Documentos procesados por pipeline: {len(updated_df)}")
        print(f"   📈 Cobertura: {(len(updated_df) / len(pd.read_csv(csv_path))) * 100:.1f}%")
        
        # Mostrar algunos ejemplos
        print("\n📋 Ejemplos de documentos procesados:")
        for i, row in updated_df.head(3).iterrows():
            print(f"   {row['document_id']} -> {row['json_path']}")
        
    except Exception as e:
        print(f"❌ Error actualizando CSV: {e}")

if __name__ == "__main__":
    main() 