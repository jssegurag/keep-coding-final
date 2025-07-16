from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IPipelineStep(ABC):
    """
    Interfaz para los pasos del pipeline de procesamiento de documentos.
    Sigue el principio de inversión de dependencias (DIP) de SOLID.
    """
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el paso del pipeline.
        
        :param input_data: Datos de entrada del paso anterior
        :return: Datos de salida para el siguiente paso
        """
        pass
    
    @abstractmethod
    def get_step_name(self) -> str:
        """
        Retorna el nombre identificador del paso.
        
        :return: Nombre del paso
        """
        pass
    
    @abstractmethod
    def get_step_description(self) -> str:
        """
        Retorna la descripción del paso.
        
        :return: Descripción del paso
        """
        pass
    
    @abstractmethod
    def can_execute(self, input_data: Dict[str, Any]) -> bool:
        """
        Verifica si el paso puede ejecutarse con los datos de entrada.
        
        :param input_data: Datos de entrada a validar
        :return: True si el paso puede ejecutarse
        """
        pass 