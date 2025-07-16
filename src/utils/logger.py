"""
Configuración de logging para el proyecto
Siguiendo principios SOLID y GRASP
"""
import logging
import os
from datetime import datetime
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configurar logger para el módulo.
    Responsabilidad única: Configuración de logging.
    
    Args:
        name: Nombre del logger
        log_file: Ruta del archivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Formato sin emojis como especifica el documento
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_validation_logger() -> logging.Logger:
    """
    Obtener logger específico para validación de embeddings.
    Responsabilidad única: Logger especializado para validación.
    
    Returns:
        Logger configurado para validación
    """
    return setup_logger(
        'embedding_validator',
        'logs/embedding_validation.log'
    )

def get_testing_logger() -> logging.Logger:
    """
    Obtener logger específico para testing.
    Responsabilidad única: Logger especializado para testing.
    
    Returns:
        Logger configurado para testing
    """
    return setup_logger(
        'testing',
        'logs/testing.log'
    ) 