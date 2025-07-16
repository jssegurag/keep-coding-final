import os
from dotenv import load_dotenv

from src.infrastructure.local_file_handler import LocalFileHandler
from src.infrastructure.docling_api_processor import DoclingApiProcessor
from src.infrastructure.pipeline_steps.ocr_step import OCRStep
from src.infrastructure.pipeline_steps.metadata_extraction_step import MetadataExtractionStep
from src.application.document_pipeline_orchestrator import DocumentPipelineOrchestrator
from src.infrastructure.pipeline_config import PipelineConfig

def create_pipeline_steps(api_base_url: str, config: PipelineConfig) -> list:
    """
    Factory method para crear los pasos del pipeline.
    Sigue el principio de responsabilidad única (SRP) - solo crea pasos.
    Implementa el principio abierto/cerrado (OCP) - extensible sin modificar.
    
    :param api_base_url: URL base de la API
    :param config: Configuración del pipeline
    :return: Lista de pasos del pipeline
    """
    pipeline_steps = []
    
    # Crear dependencias
    document_processor = DoclingApiProcessor(api_base_url=api_base_url)
    
    # Agregar pasos según la configuración
    if config.enable_ocr:
        pipeline_steps.append(OCRStep(document_processor=document_processor))
    
    if config.enable_metadata_extraction:
        pipeline_steps.append(MetadataExtractionStep())
    
    # Aquí se pueden agregar más pasos en el futuro:
    # if config.enable_legal_reference_extraction:
    #     pipeline_steps.append(LegalReferenceExtractionStep())
    # 
    # if config.enable_vectorization:
    #     pipeline_steps.append(VectorizationStep())
    # 
    # if config.enable_database_storage:
    #     pipeline_steps.append(DatabaseStorageStep())
    
    return pipeline_steps

def validate_configuration() -> tuple:
    """
    Valida la configuración del entorno.
    Sigue el principio de responsabilidad única (SRP) - solo valida configuración.
    
    :return: Tupla con (api_base_url, config) si es válida
    :raises: ValueError si la configuración no es válida
    """
    load_dotenv()
    api_base_url = os.getenv("API_BASE_URL")
    
    if not api_base_url:
        raise ValueError(
            "API_BASE_URL no está configurado. "
            "Por favor crea un archivo .env con: API_BASE_URL=http://localhost:8000"
        )
    
    # Crear configuración del pipeline
    try:
        max_workers = int(os.getenv("MAX_WORKERS", "10"))
        if max_workers <= 0:
            raise ValueError("MAX_WORKERS debe ser un número positivo")
    except (ValueError, TypeError):
        print("⚠️ MAX_WORKERS no es un número válido. Usando valor por defecto (10).")
        max_workers = 10
    
    config = PipelineConfig(
        max_workers=max_workers,
        source_directory=os.getenv("SOURCE_DIR", "src/resources/docs"),
        target_directory=os.getenv("TARGET_DIR", "target"),
        output_formats=os.getenv("OUTPUT_FORMATS", "json").split(",")
    )
    
    return api_base_url, config

def main():
    """
    Función principal que orquesta el pipeline de procesamiento de documentos.
    Sigue el principio de responsabilidad única (SRP) - solo orquesta la ejecución.
    Implementa baja acoplamiento (GRASP) - no depende de implementaciones concretas.
    """
    try:
        # 1. Validar configuración
        api_base_url, config = validate_configuration()
        
        # 2. Configurar componentes de infraestructura
        file_handler = LocalFileHandler(
            source_dir=config.source_directory, 
            target_dir=config.target_directory
        )
        
        # 3. Crear pasos del pipeline usando factory method
        pipeline_steps = create_pipeline_steps(api_base_url, config)
        
        # 4. Crear orquestador del pipeline
        pipeline_orchestrator = DocumentPipelineOrchestrator(
            file_handler=file_handler,
            pipeline_steps=pipeline_steps,
            max_workers=config.max_workers
        )
        
        # 5. Ejecutar el pipeline completo
        pipeline_orchestrator.execute_pipeline(output_formats=config.output_formats)
        
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        return
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return


if __name__ == "__main__":
    main() 