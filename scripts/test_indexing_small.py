#!/usr/bin/env python3
"""
Script de prueba para indexar un número limitado de documentos
"""
import sys
import os
import json
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing.chroma_indexer import ChromaIndexer
from config.settings import CSV_METADATA_PATH, JSON_DOCS_PATH

def main():
    print("Iniciando prueba de indexación con documentos limitados...")
    
    # Crear indexador
    indexer = ChromaIndexer()
    
    # Verificar archivos de entrada
    if not os.path.exists(CSV_METADATA_PATH):
        print(f"No se encontró el archivo CSV: {CSV_METADATA_PATH}")
        return
    
    if not os.path.exists(JSON_DOCS_PATH):
        print(f"No se encontró el directorio JSON: {JSON_DOCS_PATH}")
        return
    
    # Cargar solo los primeros 3 documentos
    df = pd.read_csv(CSV_METADATA_PATH)
    df_sample = df.head(3)
    
    print(f"Procesando {len(df_sample)} documentos de prueba...")
    
    documents_to_index = []
    
    for _, row in df_sample.iterrows():
        # Extraer nombre del archivo del path completo
        document_path = row['documentname']
        document_id = os.path.basename(document_path).replace('.pdf', '')
        
        print(f"Procesando documento: {document_id}")
        
        # Crear metadatos básicos
        metadata = {
            'document_id': document_id,
            'document_path': document_path,
            'id': row['id']
        }
        
        # Parsear respuesta JSON si existe
        if 'response' in row and pd.notna(row['response']):
            try:
                response_data = json.loads(row['response'])
                if isinstance(response_data, list):
                    # Si es una lista, tomar el primer elemento
                    response_data = response_data[0] if response_data else {}
                
                # Extraer información del demandante
                if 'demandante' in response_data:
                    demandante = response_data['demandante']
                    if demandante:
                        # Nombres y apellidos
                        nombres = demandante.get('nombresPersonaDemandante', '')
                        apellidos = demandante.get('apellidosPersonaDemandante', '')
                        nombre_empresa = demandante.get('NombreEmpresaDemandante', '')
                        
                        if nombres and apellidos:
                            metadata['demandante'] = f"{nombres} {apellidos}".strip()
                        elif nombre_empresa:
                            metadata['demandante'] = nombre_empresa
                        else:
                            metadata['demandante'] = 'No especificado'
                        
                        # Información adicional
                        metadata['tipo_identificacion'] = demandante.get('tipoIdentificacionDelDemandante', '')
                        metadata['numero_identificacion'] = demandante.get('numeroIdentificacionDelDemandante', '')
                        metadata['ciudad'] = demandante.get('ciudadDelDemandante', '')
                        metadata['departamento'] = demandante.get('DepartamentoDelDemandante', '')
                        metadata['correo'] = demandante.get('correoElectronicoDelDemandante', '')
                        metadata['direccion'] = demandante.get('direccionFisicaDelDemandante', '')
                        metadata['telefono'] = demandante.get('telefonoDelDemandante', '')
                
                # Extraer resoluciones si existen
                if 'resolucionesRadicadosNumerosReferencias' in response_data:
                    metadata['resoluciones'] = response_data['resolucionesRadicadosNumerosReferencias']
                
                # Tipo de entidad
                if 'TipoEntidadRemitente' in response_data:
                    metadata['tipo_entidad'] = response_data['TipoEntidadRemitente']
                    
            except json.JSONDecodeError as e:
                print(f"Error parseando JSON para documento {document_id}: {e}")
        
        # Cargar contenido JSON
        json_path = os.path.join(JSON_DOCS_PATH, f"{document_id}.pdf", "output.json")
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
                # Extraer texto de todos los elementos del array 'texts'
                texts_array = content.get('texts', [])
                full_text = ' '.join([t.get('text', '') for t in texts_array if t.get('text')])
            
            print(f"  - Texto extraído: {len(full_text)} caracteres")
            print(f"  - Demandante: {metadata.get('demandante', 'No especificado')}")
            
            documents_to_index.append({
                'id': document_id,
                'text': full_text,
                'metadata': metadata
            })
        else:
            print(f"  - Archivo JSON no encontrado: {json_path}")
    
    # Indexar documentos
    result = indexer.index_batch(documents_to_index)
    
    if result.get('successful', 0) > 0:
        print(f"\nPrueba completada:")
        print(f"   - Documentos procesados: {result['total_documents']}")
        print(f"   - Exitosos: {result['successful']}")
        print(f"   - Fallidos: {result['failed']}")
        print(f"   - Tasa de éxito: {result['success_rate']:.1f}%")
        
        # Mostrar estadísticas
        stats = indexer.get_collection_stats()
        print(f"\nEstadísticas de la colección:")
        print(f"   - Chunks totales: {stats['total_chunks']}")
        print(f"   - Nombre: {stats['collection_name']}")
        print(f"   - Metadatos disponibles: {', '.join(stats['sample_metadata_keys'])}")
        
        # Probar búsqueda
        print(f"\nProbando búsqueda:")
        search_results = indexer.search_similar("demandante", n_results=3)
        if 'error' not in search_results:
            print(f"   - Búsqueda exitosa: {search_results['total_found']} resultados")
        else:
            print(f"   - Error en búsqueda: {search_results['error']}")
        
    else:
        print(f"Error en indexación: {result}")

if __name__ == "__main__":
    main() 