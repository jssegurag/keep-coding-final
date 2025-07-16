from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    """
    Configuración del pipeline de procesamiento de documentos.
    Sigue el principio de responsabilidad única (SRP) - solo maneja configuración.
    """
    
    # Configuración de archivos
    source_directory: str = 'src/resources/docs'
    target_directory: str = 'target'
    
    # Configuración de procesamiento
    max_workers: int = 10
    output_formats: List[str] = None
    
    # Configuración de pasos
    enable_ocr: bool = True
    enable_metadata_extraction: bool = True
    enable_legal_reference_extraction: bool = False
    enable_vectorization: bool = False
    enable_database_storage: bool = False
    
    def __post_init__(self):
        """
        Inicialización post-constructor para validar configuración.
        """
        if self.output_formats is None:
            self.output_formats = ["json"]
        
        if self.max_workers <= 0:
            raise ValueError("max_workers debe ser un número positivo")
    
    def get_enabled_steps(self) -> List[str]:
        """
        Retorna la lista de pasos habilitados.
        
        :return: Lista de nombres de pasos habilitados
        """
        enabled_steps = []
        
        if self.enable_ocr:
            enabled_steps.append("ocr_extraction")
        
        if self.enable_metadata_extraction:
            enabled_steps.append("metadata_extraction")
        
        if self.enable_legal_reference_extraction:
            enabled_steps.append("legal_reference_extraction")
        
        if self.enable_vectorization:
            enabled_steps.append("vectorization")
        
        if self.enable_database_storage:
            enabled_steps.append("database_storage")
        
        return enabled_steps
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la configuración a diccionario.
        
        :return: Diccionario con la configuración
        """
        return {
            'source_directory': self.source_directory,
            'target_directory': self.target_directory,
            'max_workers': self.max_workers,
            'output_formats': self.output_formats,
            'enabled_steps': self.get_enabled_steps(),
            'step_configuration': {
                'ocr': self.enable_ocr,
                'metadata_extraction': self.enable_metadata_extraction,
                'legal_reference_extraction': self.enable_legal_reference_extraction,
                'vectorization': self.enable_vectorization,
                'database_storage': self.enable_database_storage
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PipelineConfig':
        """
        Crea una instancia de PipelineConfig desde un diccionario.
        Factory method que sigue el principio de responsabilidad única.
        
        :param config_dict: Diccionario con la configuración
        :return: Instancia de PipelineConfig
        """
        return cls(
            source_directory=config_dict.get('source_directory', 'src/resources/docs'),
            target_directory=config_dict.get('target_directory', 'target'),
            max_workers=config_dict.get('max_workers', 10),
            output_formats=config_dict.get('output_formats', ["json"]),
            enable_ocr=config_dict.get('step_configuration', {}).get('ocr', True),
            enable_metadata_extraction=config_dict.get('step_configuration', {}).get('metadata_extraction', True),
            enable_legal_reference_extraction=config_dict.get('step_configuration', {}).get('legal_reference_extraction', False),
            enable_vectorization=config_dict.get('step_configuration', {}).get('vectorization', False),
            enable_database_storage=config_dict.get('step_configuration', {}).get('database_storage', False)
        ) 