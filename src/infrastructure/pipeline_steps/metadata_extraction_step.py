import os
import json
from typing import Dict, Any
from src.domain.i_pipeline_step import IPipelineStep

class MetadataExtractionStep(IPipelineStep):
    """
    Segundo paso del pipeline: Extracción de metadata del documento.
    Sigue el principio de responsabilidad única (SRP) - solo extrae metadata.
    Implementa el principio abierto/cerrado (OCP) - extensible sin modificar.
    """
    
    def __init__(self):
        """
        Constructor sin dependencias externas para baja acoplamiento.
        """
        pass
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la extracción de metadata.
        
        :param input_data: Debe contener 'file_path' y 'ocr_results'
        :return: Datos enriquecidos con metadata extraída
        """
        if not self.can_execute(input_data):
            raise ValueError(f"No se puede ejecutar {self.get_step_name()} con los datos proporcionados")
        
        file_path = input_data['file_path']
        ocr_results = input_data.get('ocr_results', {})
        original_filename = input_data.get('original_filename', os.path.basename(file_path))
        
        # Verificar si los datos vienen del cache
        cache_used = input_data.get('step_results', {}).get('ocr', {}).get('cache_used', False)
        
        if cache_used:
            print(f"📊 [Metadata] Extrayendo metadata desde cache: {original_filename}")
        else:
            print(f"📊 [Metadata] Extrayendo metadata de: {original_filename}")
        
        # Extraer metadata del archivo
        file_metadata = self._extract_file_metadata(file_path)
        
        # Extraer metadata del contenido OCR
        content_metadata = self._extract_content_metadata(ocr_results)
        
        # Combinar metadata
        combined_metadata = {
            **file_metadata,
            **content_metadata
        }
        
        # Enriquecer los datos de entrada
        result = input_data.copy()
        result['metadata'] = combined_metadata
        result['step_results']['metadata_extraction'] = {
            'status': 'completed',
            'metadata_extracted': bool(combined_metadata),
            'file_metadata_keys': list(file_metadata.keys()),
            'content_metadata_keys': list(content_metadata.keys()),
            'cache_used': cache_used
        }
        
        if cache_used:
            print(f"✅ [Metadata] Completado desde cache: {original_filename}")
        else:
            print(f"✅ [Metadata] Completado: {original_filename}")
        
        return result
    
    def get_step_name(self) -> str:
        return "metadata_extraction"
    
    def get_step_description(self) -> str:
        return "Extracción de metadata del documento y contenido OCR"
    
    def can_execute(self, input_data: Dict[str, Any]) -> bool:
        """
        Verifica si el paso puede ejecutarse con los datos de entrada.
        
        :param input_data: Datos de entrada a validar
        :return: True si el paso puede ejecutarse
        """
        # Necesita file_path y ocr_results
        file_path = input_data.get('file_path')
        ocr_results = input_data.get('ocr_results')
        
        if not file_path or not os.path.exists(file_path):
            return False
        
        if not ocr_results:
            return False
        
        return True
    
    def _extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extrae metadata del archivo físico.
        Método privado que encapsula la lógica de extracción de metadata del archivo.
        
        :param file_path: Ruta del archivo
        :return: Metadata del archivo
        """
        try:
            stat = os.stat(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            return {
                'filename': os.path.basename(file_path),
                'filepath': file_path,
                'file_size': stat.st_size,
                'file_extension': file_ext,
                'creation_date': stat.st_ctime,
                'modification_date': stat.st_mtime,
                'access_date': stat.st_atime
            }
        except Exception as e:
            print(f"⚠️ Error extrayendo metadata del archivo: {e}")
            return {}
    
    def _extract_content_metadata(self, ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae metadata del contenido OCR.
        Método privado que encapsula la lógica de extracción de metadata del contenido.
        
        :param ocr_results: Resultados del OCR
        :return: Metadata del contenido
        """
        try:
            content_metadata = {
                'ocr_formats_available': list(ocr_results.keys()),
                'has_json_content': 'json' in ocr_results,
                'has_text_content': 'text' in ocr_results,
                'has_html_content': 'html' in ocr_results
            }
            
            # Si hay contenido JSON, intentar extraer metadata adicional
            if 'json' in ocr_results:
                json_content = ocr_results['json']
                if isinstance(json_content, str):
                    try:
                        json_data = json.loads(json_content)
                        content_metadata.update(self._extract_json_metadata(json_data))
                    except json.JSONDecodeError:
                        pass
                elif isinstance(json_content, dict):
                    content_metadata.update(self._extract_json_metadata(json_content))
            
            return content_metadata
            
        except Exception as e:
            print(f"⚠️ Error extrayendo metadata del contenido: {e}")
            return {}
    
    def _extract_json_metadata(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae metadata específica del JSON de Docling.
        Método privado que encapsula la lógica de extracción de metadata JSON.
        
        :param json_data: Datos JSON del documento
        :return: Metadata extraída del JSON
        """
        metadata = {}
        
        try:
            # Extraer información de estructura del documento
            if 'texts' in json_data:
                metadata['text_elements_count'] = len(json_data['texts'])
            
            if 'tables' in json_data:
                metadata['table_elements_count'] = len(json_data['tables'])
            
            if 'pictures' in json_data:
                metadata['picture_elements_count'] = len(json_data['pictures'])
            
            if 'groups' in json_data:
                metadata['group_elements_count'] = len(json_data['groups'])
            
            # Calcular estadísticas de confianza si están disponibles
            if 'texts' in json_data and json_data['texts']:
                confidences = [text.get('confidence', 0) for text in json_data['texts']]
                if confidences:
                    metadata['avg_confidence'] = sum(confidences) / len(confidences)
                    metadata['min_confidence'] = min(confidences)
                    metadata['max_confidence'] = max(confidences)
            
        except Exception as e:
            print(f"⚠️ Error extrayendo metadata JSON: {e}")
        
        return metadata 