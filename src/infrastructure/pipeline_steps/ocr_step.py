import os
from typing import Dict, Any
from src.domain.i_pipeline_step import IPipelineStep
from src.infrastructure.docling_api_processor import DoclingApiProcessor

class OCRStep(IPipelineStep):
    """
    Primer paso del pipeline: Extracción de texto mediante OCR.
    Sigue el principio de responsabilidad única (SRP) - solo se encarga del OCR.
    Incluye verificación de cache para evitar reprocesamiento.
    """
    
    def __init__(self, document_processor: DoclingApiProcessor):
        """
        Constructor que recibe la dependencia inyectada (DIP).
        
        :param document_processor: Procesador de documentos inyectado
        """
        self.document_processor = document_processor
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el paso de OCR con verificación de cache.
        
        :param input_data: Debe contener 'file_path' y 'output_formats'
        :return: Datos procesados con el contenido extraído
        """
        if not self.can_execute(input_data):
            raise ValueError(f"No se puede ejecutar {self.get_step_name()} con los datos proporcionados")
        
        file_path = input_data['file_path']
        output_formats = input_data.get('output_formats', ['json'])
        file_handler = input_data.get('file_handler')
        original_filename = os.path.basename(file_path)
        
        print(f"🔍 [OCR] Verificando: {original_filename}")
        
        # Verificar si ya existe en cache
        if file_handler and file_handler.is_document_processed(original_filename, output_formats):
            print(f"📋 [OCR] Cache encontrado para: {original_filename}")
            
            # Cargar resultados existentes
            cached_results = file_handler.load_existing_results(original_filename, output_formats)
            if cached_results:
                print(f"✅ [OCR] Cargado desde cache: {original_filename}")
                
                # Preparar resultado con datos del cache
                result = {
                    'file_path': file_path,
                    'original_filename': original_filename,
                    'ocr_results': cached_results,
                    'output_formats': output_formats,
                    'step_results': {
                        'ocr': {
                            'status': 'completed_from_cache',
                            'formats_processed': list(cached_results.keys()),
                            'content_available': bool(cached_results),
                            'cache_used': True
                        }
                    }
                }
                
                return result
        
        # Si no existe en cache, procesar normalmente
        print(f"🔄 [OCR] Procesando: {original_filename}")
        
        # Procesar documento con OCR
        processed_content = self.document_processor.process(file_path, output_formats)
        
        # Preparar resultado para el siguiente paso
        result = {
            'file_path': file_path,
            'original_filename': original_filename,
            'ocr_results': processed_content,
            'output_formats': output_formats,
            'step_results': {
                'ocr': {
                    'status': 'completed',
                    'formats_processed': list(processed_content.keys()),
                    'content_available': bool(processed_content),
                    'cache_used': False
                }
            }
        }
        
        print(f"✅ [OCR] Completado: {original_filename}")
        return result
    
    def get_step_name(self) -> str:
        return "ocr_extraction"
    
    def get_step_description(self) -> str:
        return "Extracción de texto mediante OCR usando Docling API con cache"
    
    def can_execute(self, input_data: Dict[str, Any]) -> bool:
        """
        Verifica si el paso puede ejecutarse con los datos de entrada.
        
        :param input_data: Datos de entrada a validar
        :return: True si el paso puede ejecutarse
        """
        file_path = input_data.get('file_path')
        if not file_path:
            return False
        
        if not os.path.exists(file_path):
            return False
        
        # Verificar que el archivo sea procesable
        valid_extensions = ['.pdf', '.tiff', '.tif', '.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        return file_ext in valid_extensions 