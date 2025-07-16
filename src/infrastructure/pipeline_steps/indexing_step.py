"""
Paso de indexación del pipeline: Indexación de documentos en ChromaDB.
Sigue el principio de responsabilidad única (SRP) - solo se encarga de la indexación.
Implementa el principio abierto/cerrado (OCP) - extensible sin modificar.
Incluye verificación de cache para evitar re-indexación.
"""
import os
import json
import pandas as pd
from typing import Dict, Any, List
from src.domain.i_pipeline_step import IPipelineStep
from src.indexing.chroma_indexer import ChromaIndexer
from config.settings import CSV_METADATA_PATH, JSON_DOCS_PATH

class IndexingStep(IPipelineStep):
    """
    Paso de indexación del pipeline: Indexa documentos procesados en ChromaDB.
    Sigue el principio de responsabilidad única (SRP) - solo se encarga de la indexación.
    Implementa el principio abierto/cerrado (OCP) - extensible sin modificar.
    Incluye verificación de cache para evitar re-indexación.
    """
    
    def __init__(self, indexer: ChromaIndexer = None):
        """
        Constructor con inyección de dependencias (DIP).
        
        :param indexer: Indexador de ChromaDB inyectado (opcional para testing)
        """
        self.indexer = indexer or ChromaIndexer()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el paso de indexación.
        
        :param input_data: Debe contener información del pipeline anterior
        :return: Datos enriquecidos con resultados de indexación
        """
        if not self.can_execute(input_data):
            raise ValueError(f"No se puede ejecutar {self.get_step_name()} con los datos proporcionados")
        
        print(f"🔍 [Indexing] Iniciando indexación de documentos procesados...")
        
        try:
            # Ejecutar indexación usando el método existente
            result = self.indexer.load_and_index_from_csv()
            
            # Preparar resultado para el siguiente paso
            indexing_result = {
                'status': 'completed' if result.get('successful', 0) > 0 else 'failed',
                'total_documents': result.get('total_documents', 0),
                'successful': result.get('successful', 0),
                'failed': result.get('failed', 0),
                'success_rate': result.get('success_rate', 0),
                'error': result.get('error') if result.get('successful', 0) == 0 else None
            }
            
            # Enriquecer los datos de entrada
            result_data = input_data.copy()
            result_data['indexing_results'] = result
            result_data['step_results']['indexing'] = indexing_result
            
            if indexing_result['status'] == 'completed':
                print(f"✅ [Indexing] Completado: {indexing_result['successful']} documentos indexados")
            else:
                print(f"❌ [Indexing] Falló: {indexing_result.get('error', 'Sin detalles')}")
            
            return result_data
            
        except Exception as e:
            print(f"❌ [Indexing] Error: {e}")
            # Preparar resultado de error
            error_result = input_data.copy()
            error_result['step_results']['indexing'] = {
                'status': 'failed',
                'error': str(e),
                'total_documents': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0
            }
            return error_result
    
    def get_step_name(self) -> str:
        return "document_indexing"
    
    def get_step_description(self) -> str:
        return "Indexación de documentos procesados en ChromaDB para búsqueda semántica"
    
    def can_execute(self, input_data: Dict[str, Any]) -> bool:
        """
        Verifica si el paso puede ejecutarse con los datos de entrada.
        
        :param input_data: Datos de entrada a validar
        :return: True si el paso puede ejecutarse
        """
        # Verificar que existan los archivos necesarios
        if not os.path.exists(CSV_METADATA_PATH):
            print(f"⚠️ [Indexing] CSV de metadatos no encontrado: {CSV_METADATA_PATH}")
            return False
        
        if not os.path.exists(JSON_DOCS_PATH):
            print(f"⚠️ [Indexing] Directorio de documentos JSON no encontrado: {JSON_DOCS_PATH}")
            return False
        
        # Verificar que haya documentos procesados
        try:
            df = pd.read_csv(CSV_METADATA_PATH)
            if len(df) == 0:
                print(f"⚠️ [Indexing] CSV de metadatos está vacío")
                return False
        except Exception as e:
            print(f"⚠️ [Indexing] Error leyendo CSV: {e}")
            return False
        
        return True 