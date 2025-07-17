import os
import json
from typing import Dict, Any, List, Optional
from src.domain.i_pipeline_step import IPipelineStep

class MetadataExtractionStep(IPipelineStep):
    """
    Segundo paso del pipeline: Extracción universal de metadata del documento.
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
        Ejecuta la extracción universal de metadata.
        
        :param input_data: Debe contener 'file_path' y 'ocr_results'
        :return: Datos enriquecidos con metadata extraída universalmente
        """
        if not self.can_execute(input_data):
            raise ValueError(f"No se puede ejecutar {self.get_step_name()} con los datos proporcionados")
        
        file_path = input_data['file_path']
        ocr_results = input_data.get('ocr_results', {})
        original_filename = input_data.get('original_filename', os.path.basename(file_path))
        
        # Verificar si los datos vienen del cache
        cache_used = input_data.get('step_results', {}).get('ocr', {}).get('cache_used', False)
        
        if cache_used:
            print(f"📊 [Metadata] Extrayendo metadata universal desde cache: {original_filename}")
        else:
            print(f"📊 [Metadata] Extrayendo metadata universal de: {original_filename}")
        
        # Extraer metadata del archivo
        file_metadata = self._extract_file_metadata(file_path)
        
        # Extraer metadata universal del contenido OCR
        content_metadata = self._extract_universal_content_metadata(ocr_results)
        
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
            'total_metadata_fields': len(combined_metadata),
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
        return "Extracción universal de metadata del documento y contenido OCR"
    
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
    
    def _extract_universal_content_metadata(self, ocr_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae metadata universal del contenido OCR.
        Método privado que encapsula la lógica de extracción universal de metadata del contenido.
        
        :param ocr_results: Resultados del OCR
        :return: Metadata universal del contenido
        """
        try:
            content_metadata = {
                'ocr_formats_available': list(ocr_results.keys()),
                'has_json_content': 'json' in ocr_results,
                'has_text_content': 'text' in ocr_results,
                'has_html_content': 'html' in ocr_results
            }
            
            # Si hay contenido JSON, extraer TODOS los metadatos recursivamente
            if 'json' in ocr_results:
                json_content = ocr_results['json']
                if isinstance(json_content, str):
                    try:
                        # Reparar y parsear JSON
                        json_data = self._repair_and_parse_json(json_content)
                        if json_data:
                            # Extraer TODOS los metadatos recursivamente
                            universal_metadata = self._extract_all_metadata_recursive(json_data)
                            content_metadata.update(universal_metadata)
                    except Exception as e:
                        print(f"⚠️ Error procesando JSON string: {e}")
                elif isinstance(json_content, dict):
                    # Extraer TODOS los metadatos recursivamente
                    universal_metadata = self._extract_all_metadata_recursive(json_content)
                    content_metadata.update(universal_metadata)
            
            return content_metadata
            
        except Exception as e:
            print(f"⚠️ Error extrayendo metadata universal del contenido: {e}")
            return {}
    
    def _repair_and_parse_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """
        Repara y parsea JSON mal formateado.
        Método privado que encapsula la lógica de reparación de JSON.
        
        :param json_str: String JSON a reparar
        :return: Diccionario parseado o None si falla
        """
        try:
            # Intentar parseo directo
            return json.loads(json_str)
        except json.JSONDecodeError:
            try:
                # Intentar reparar JSON básico
                repaired_json = self._basic_json_repair(json_str)
                return json.loads(repaired_json)
            except Exception as e:
                print(f"⚠️ Error reparando JSON: {e}")
                return None
    
    def _basic_json_repair(self, json_str: str) -> str:
        """
        Reparación básica de JSON mal formateado.
        Método privado que encapsula la lógica de reparación básica.
        
        :param json_str: String JSON a reparar
        :return: String JSON reparado
        """
        # Reparaciones básicas comunes
        repaired = json_str.strip()
        
        # Remover caracteres de control
        repaired = ''.join(char for char in repaired if ord(char) >= 32 or char in '\n\r\t')
        
        # Corregir comillas mal escapadas
        repaired = repaired.replace('\\"', '"').replace('""', '"')
        
        # Corregir comas finales antes de llaves de cierre
        import re
        repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
        
        # Corregir comas finales antes de llaves de apertura
        repaired = re.sub(r',(\s*[{[])', r'\1', repaired)
        
        return repaired
    
    def _extract_all_metadata_recursive(self, json_data: Any, prefix: str = "") -> Dict[str, Any]:
        """
        Extrae recursivamente TODOS los metadatos de cualquier estructura JSON.
        Método privado que encapsula la lógica de extracción recursiva.
        Sigue SRP - solo extrae metadatos.
        
        :param json_data: Datos JSON a procesar
        :param prefix: Prefijo para nombres de campos anidados
        :return: Diccionario con todos los metadatos extraídos
        """
        metadata = {}
        
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                normalized_key = self._normalize_field_name(key, prefix)
                if isinstance(value, (dict, list)):
                    # Recursión para estructuras anidadas
                    nested_metadata = self._extract_all_metadata_recursive(value, normalized_key)
                    metadata.update(nested_metadata)
                else:
                    metadata[normalized_key] = value
        elif isinstance(json_data, list):
            for i, item in enumerate(json_data):
                nested_metadata = self._extract_all_metadata_recursive(item, f"{prefix}_{i}")
                metadata.update(nested_metadata)
        
        return metadata
    
    def _normalize_field_name(self, field_name: str, prefix: str = "") -> str:
        """
        Normaliza el nombre de un campo para consistencia.
        Método privado que encapsula la lógica de normalización de nombres.
        
        :param field_name: Nombre del campo a normalizar
        :param prefix: Prefijo opcional
        :return: Nombre normalizado
        """
        import unicodedata
        import re
        # Eliminar tildes primero
        nfkd = unicodedata.normalize('NFKD', field_name)
        no_tildes = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        # Insertar guiones bajos antes de mayúsculas (camelCase)
        snake = re.sub(r'([a-z])([A-Z])', r'\1_\2', no_tildes)
        # Convertir a minúsculas
        snake = snake.lower()
        # Reemplazar caracteres no alfanuméricos por guion bajo
        snake = ''.join(c if c.isalnum() else '_' for c in snake)
        # Remover múltiples guiones bajos
        snake = re.sub(r'_+', '_', snake)
        # Remover guiones bajos al inicio y final
        snake = snake.strip('_')
        # Añadir prefijo si existe
        if prefix:
            snake = f"{prefix}_{snake}"
        return snake
    
    def _extract_json_metadata(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae metadata específica del JSON de Docling (método legacy para compatibilidad).
        Método privado que encapsula la lógica de extracción de metadata JSON específica.
        
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
            print(f"⚠️ Error extrayendo metadata JSON específica: {e}")
        
        return metadata 