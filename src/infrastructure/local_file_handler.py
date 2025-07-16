import os
import json
from typing import Dict, List

from src.domain.i_file_handler import IFileHandler

class LocalFileHandler(IFileHandler):
    """
    A concrete implementation of IFileHandler that interacts with the local
    file system.
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
                print(f"Successfully saved {file_path}")
            except (IOError, TypeError) as e:
                print(f"Error saving file {file_path}: {e}") 