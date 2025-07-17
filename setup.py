#!/usr/bin/env python3
"""
Script de configuración inicial del proyecto RAG.

Responsable de configurar el entorno de desarrollo siguiendo
principios de responsabilidad única y manejo robusto de errores.
"""

import subprocess
import sys
import os
import logging
from typing import List, Optional
from pathlib import Path

# Configurar logging sin emojis según reglas solid-grasp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SetupError(Exception):
    """Excepción personalizada para errores de configuración."""
    pass


class EnvironmentSetup:
    """Clase responsable de configurar el entorno de desarrollo."""
    
    def __init__(self) -> None:
        """Inicializar el configurador de entorno."""
        self.directories: List[str] = [
            "src/chunking", "src/indexing", "src/query", "src/testing", "src/utils",
            "src/resources/metadata",
            "data/raw", "data/processed", "data/chroma_db",
            "tests/unit", "tests/integration",
            "config", "logs"
        ]
    
    def create_directories(self) -> None:
        """Crear estructura de directorios del proyecto."""
        logger.info("Creando estructura de directorios")
        
        for directory in self.directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"Directorio creado: {directory}")
            except OSError as e:
                error_msg = f"Error al crear directorio {directory}: {e}"
                logger.error(error_msg)
                raise SetupError(error_msg) from e
    
    def install_requirements(self) -> None:
        """Instalar dependencias del proyecto."""
        logger.info("Instalando dependencias del proyecto")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info("Dependencias instaladas correctamente")
        except subprocess.CalledProcessError as e:
            error_msg = f"Error al instalar dependencias: {e}"
            logger.error(error_msg)
            raise SetupError(error_msg) from e
        except FileNotFoundError:
            error_msg = "No se encontró el archivo requirements.txt"
            logger.error(error_msg)
            raise SetupError(error_msg)
    
    def validate_configuration(self) -> None:
        """Validar que la configuración se puede cargar correctamente."""
        logger.info("Validando configuración")
        
        try:
            from config.settings import (
                GOOGLE_API_KEY, EMBEDDING_MODEL, CHUNK_SIZE, 
                CHROMA_PERSIST_DIRECTORY
            )
            logger.info("Configuración cargada correctamente")
        except ImportError as e:
            error_msg = f"Error al cargar configuración: {e}"
            logger.error(error_msg)
            raise SetupError(error_msg) from e
    
    def create_env_template(self) -> None:
        """Crear plantilla de archivo .env si no existe."""
        env_path = Path(".env")
        if not env_path.exists():
            logger.info("Creando plantilla de archivo .env")
            try:
                with open(env_path, "w") as f:
                    f.write("GOOGLE_API_KEY=tu_api_key_aqui\n")
                logger.info("Plantilla .env creada")
            except IOError as e:
                error_msg = f"Error al crear archivo .env: {e}"
                logger.error(error_msg)
                raise SetupError(error_msg) from e
    
    def run(self) -> None:
        """Ejecutar configuración completa del entorno."""
        logger.info("Iniciando configuración del entorno de desarrollo RAG")
        
        try:
            self.create_directories()
            self.install_requirements()
            self.validate_configuration()
            self.create_env_template()
            logger.info("Configuración completada exitosamente")
        except SetupError:
            logger.error("Configuración falló")
            sys.exit(1)


def main() -> None:
    """Función principal del script de configuración."""
    setup = EnvironmentSetup()
    setup.run()


if __name__ == "__main__":
    main() 