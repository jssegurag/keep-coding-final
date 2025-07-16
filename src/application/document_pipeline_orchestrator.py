import os
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.domain.i_pipeline_step import IPipelineStep
from src.domain.i_file_handler import IFileHandler

class DocumentPipelineOrchestrator:
    """
    Orquestador principal del pipeline de procesamiento de documentos.
    Sigue el principio de responsabilidad única (SRP) - solo orquesta la ejecución.
    Implementa alta cohesión (GRASP) - todas las responsabilidades están relacionadas.
    Incluye optimización de cache para evitar reprocesamiento.
    """
    
    def __init__(self, file_handler: IFileHandler, pipeline_steps: List[IPipelineStep], max_workers: int = 10):
        """
        Constructor con inyección de dependencias (DIP).
        
        :param file_handler: Manejador de archivos inyectado
        :param pipeline_steps: Lista de pasos del pipeline
        :param max_workers: Número máximo de workers para procesamiento paralelo
        """
        self.file_handler = file_handler
        self.pipeline_steps = pipeline_steps
        self.max_workers = max_workers
    
    def _execute_pipeline_for_document(self, file_path: str, output_formats: List[str]) -> Dict[str, Any]:
        """
        Ejecuta todo el pipeline para un documento específico.
        Método privado que encapsula la lógica de ejecución (encapsulation).
        
        :param file_path: Ruta del archivo a procesar
        :param output_formats: Formatos de salida deseados
        :return: Resultados del pipeline completo
        """
        try:
            print(f"🚀 Iniciando pipeline para: {os.path.basename(file_path)}")
            
            # Datos iniciales para el primer paso
            current_data = {
                'file_path': file_path,
                'output_formats': output_formats,
                'file_handler': self.file_handler  # Pasar file_handler para cache
            }
            
            # Ejecutar cada paso del pipeline en secuencia
            for i, step in enumerate(self.pipeline_steps, 1):
                print(f"📋 Paso {i}/{len(self.pipeline_steps)}: {step.get_step_name()}")
                
                # Verificar si el paso puede ejecutarse
                if not step.can_execute(current_data):
                    print(f"⚠️ Paso {i} no puede ejecutarse: {step.get_step_name()}")
                    current_data['step_results'][step.get_step_name()] = {
                        'status': 'skipped',
                        'reason': 'Cannot execute with current data'
                    }
                    continue
                
                try:
                    current_data = step.execute(current_data)
                    print(f"✅ Paso {i} completado: {step.get_step_name()}")
                except Exception as e:
                    print(f"❌ Error en paso {i} ({step.get_step_name()}): {e}")
                    # Agregar información del error al resultado
                    current_data['step_results'][step.get_step_name()] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    break
            
            # Guardar resultados finales si hay contenido OCR y no viene del cache
            if current_data.get('ocr_results') and not current_data.get('step_results', {}).get('ocr', {}).get('cache_used', False):
                original_name = os.path.basename(file_path)
                self.file_handler.save_results(original_name, current_data['ocr_results'])
            
            return current_data
            
        except Exception as e:
            print(f"❌ Error general en pipeline para {os.path.basename(file_path)}: {e}")
            return {
                'file_path': file_path,
                'status': 'failed',
                'error': str(e)
            }
    
    def execute_pipeline(self, output_formats: List[str]):
        """
        Ejecuta el pipeline completo para todos los documentos encontrados.
        Método público que expone la funcionalidad principal (interface segregation).
        Incluye optimización de cache para evitar reprocesamiento.
        
        :param output_formats: Formatos de salida deseados
        """
        print("🎯 Iniciando pipeline de procesamiento de documentos...")
        self._print_pipeline_configuration()
        
        # Usar el nuevo método que filtra documentos ya procesados
        documents_to_process = self.file_handler.get_documents_to_process(output_formats)
        
        if not documents_to_process:
            print("🎉 ¡Todos los documentos ya han sido procesados!")
            return
        
        print(f"📄 Documentos por procesar: {len(documents_to_process)}")
        
        # Procesar documentos en paralelo
        self._process_documents_parallel(documents_to_process, output_formats)
    
    def _print_pipeline_configuration(self):
        """
        Imprime la configuración del pipeline.
        Método privado para encapsular la lógica de logging.
        """
        print(f"⚙️ Pasos configurados: {len(self.pipeline_steps)}")
        for i, step in enumerate(self.pipeline_steps, 1):
            print(f"   {i}. {step.get_step_name()}: {step.get_step_description()}")
    
    def _process_documents_parallel(self, documents_to_process: List[str], output_formats: List[str]):
        """
        Procesa documentos en paralelo usando ThreadPoolExecutor.
        Método privado que encapsula la lógica de procesamiento paralelo.
        
        :param documents_to_process: Lista de documentos a procesar
        :param output_formats: Formatos de salida deseados
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            print(f"⚡ Procesando con hasta {self.max_workers} workers...")
            
            future_to_doc = {
                executor.submit(self._execute_pipeline_for_document, doc, output_formats): doc
                for doc in documents_to_process
            }
            
            completed = 0
            failed = 0
            cached = 0
            
            for future in as_completed(future_to_doc):
                doc_path = future_to_doc[future]
                try:
                    result = future.result()
                    completed += 1
                    
                    if result.get('status') == 'failed':
                        failed += 1
                        print(f"❌ Falló: {os.path.basename(doc_path)}")
                    else:
                        # Verificar si se usó cache
                        ocr_status = result.get('step_results', {}).get('ocr', {})
                        if ocr_status.get('cache_used', False):
                            cached += 1
                            print(f"📋 Cache usado: {os.path.basename(doc_path)}")
                        else:
                            print(f"✅ Completado: {os.path.basename(doc_path)}")
                        
                except Exception as exc:
                    failed += 1
                    print(f"❌ Excepción en {os.path.basename(doc_path)}: {exc}")
            
            self._print_final_summary(completed, failed, cached, len(documents_to_process))
    
    def _print_final_summary(self, completed: int, failed: int, cached: int, total: int):
        """
        Imprime el resumen final del procesamiento.
        Método privado para encapsular la lógica de reporting.
        
        :param completed: Número de documentos completados exitosamente
        :param failed: Número de documentos que fallaron
        :param cached: Número de documentos que usaron cache
        :param total: Número total de documentos procesados
        """
        print("=" * 50)
        print(f"🎉 Pipeline completado.")
        print(f"📊 Resumen:")
        print(f"   ✅ Nuevos procesados: {completed - cached}")
        print(f"   📋 Cache utilizados: {cached}")
        print(f"   ❌ Fallidos: {failed}")
        print(f"   📄 Total en esta ejecución: {total}")
        if total > 0:
            success_rate = ((completed - failed) / total) * 100
            print(f"   📈 Tasa de éxito: {success_rate:.1f}%")
        else:
            print(f"   📈 Tasa de éxito: 0%") 