import os
import json
from typing import Dict, List, Optional

from src.domain.i_file_handler import IFileHandler

class LocalFileHandler(IFileHandler):
    """
    A concrete implementation of IFileHandler that interacts with the local
    file system with caching capabilities to avoid reprocessing.
    """
    def __init__(self, source_dir: str = 'src/resources/docs', target_dir: str = 'target'):
        self.source_dir = source_dir
        self.target_dir = target_dir
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

    def find_documents(self) -> List[str]:
        """
        Finds all PDF files in the source directory and subdirectories.
        """
        if not os.path.isdir(self.source_dir):
            print(f"Source directory '{self.source_dir}' not found.")
            return []
        
        pdf_files = []
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        print(f"Found {len(pdf_files)} PDF files to process")
        return pdf_files

    def is_document_processed(self, original_document_name: str, output_formats: List[str]) -> bool:
        """
        Checks if a document has already been processed with the specified output formats.
        
        :param original_document_name: The name of the original document
        :param output_formats: List of output formats to check
        :return: True if the document has been processed with all specified formats
        """
        doc_folder_name = os.path.basename(original_document_name)
        output_path = os.path.join(self.target_dir, doc_folder_name)
        
        if not os.path.exists(output_path):
            return False
        
        # Check if all required output formats exist
        for format_ext in output_formats:
            file_name = f"output.{format_ext}"
            file_path = os.path.join(output_path, file_name)
            if not os.path.exists(file_path):
                return False
        
        return True

    def load_existing_results(self, original_document_name: str, output_formats: List[str]) -> Optional[Dict[str, str]]:
        """
        Loads existing results for a document if they exist.
        
        :param original_document_name: The name of the original document
        :param output_formats: List of output formats to load
        :return: Dictionary with existing results or None if not found
        """
        if not self.is_document_processed(original_document_name, output_formats):
            return None
        
        doc_folder_name = os.path.basename(original_document_name)
        output_path = os.path.join(self.target_dir, doc_folder_name)
        results = {}
        
        try:
            for format_ext in output_formats:
                file_name = f"output.{format_ext}"
                file_path = os.path.join(output_path, file_name)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    if format_ext == 'json':
                        # Load JSON as dictionary
                        results[format_ext] = json.load(f)
                    else:
                        # Load as string
                        results[format_ext] = f.read()
            
            return results
        except Exception as e:
            print(f"Error loading existing results for {original_document_name}: {e}")
            return None

    def get_documents_to_process(self, output_formats: List[str]) -> List[str]:
        """
        Finds documents that need to be processed (not already in cache).
        
        :param output_formats: List of output formats to check
        :return: List of document paths that need processing
        """
        all_documents = self.find_documents()
        documents_to_process = []
        cached_count = 0
        
        for doc_path in all_documents:
            original_name = os.path.basename(doc_path)
            
            if self.is_document_processed(original_name, output_formats):
                cached_count += 1
                print(f"📋 [Cache] Ya procesado: {original_name}")
            else:
                documents_to_process.append(doc_path)
        
        print(f"📊 [Cache] Resumen:")
        print(f"   📄 Total documentos: {len(all_documents)}")
        print(f"   ✅ Ya procesados: {cached_count}")
        print(f"   🔄 Por procesar: {len(documents_to_process)}")
        
        return documents_to_process

    def save_results(self, original_document_name: str, results: Dict[str, str]):
        """
        Saves the processed content into the target directory.
        It creates a subdirectory with the original document name.
        """
        doc_folder_name = os.path.basename(original_document_name)
        output_path = os.path.join(self.target_dir, doc_folder_name)
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for format_ext, content in results.items():
            file_name = f"output.{format_ext}"
            file_path = os.path.join(output_path, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if isinstance(content, dict):
                        json.dump(content, f, ensure_ascii=False, indent=4)
                    else:
                        f.write(str(content))
                print(f"💾 Guardado: {file_path}")
            except (IOError, TypeError) as e:
                print(f"❌ Error guardando archivo {file_path}: {e}") 