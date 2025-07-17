from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class IFileHandler(ABC):
    """
    Defines the contract for handling file system operations, such as
    finding documents to process and saving the results.
    """

    @abstractmethod
    def find_documents(self) -> List[str]:
        """
        Finds all document file paths in the source directory.

        :return: A list of absolute paths to the document files.
        """
        pass

    @abstractmethod
    def save_results(self, original_document_name: str, results: Dict[str, str]):
        """
        Saves the processed results to the file system.

        :param original_document_name: The name of the original document,
                                       used for creating the output directory.
        :param results: A dictionary where keys are the format (e.g., 'md')
                        and values are the content to be saved.
        """
        pass
    
    @abstractmethod
    def is_document_processed(self, original_document_name: str, output_formats: List[str]) -> bool:
        """
        Checks if a document has already been processed with the specified output formats.
        
        :param original_document_name: The name of the original document
        :param output_formats: List of output formats to check
        :return: True if the document has been processed with all specified formats
        """
        pass
    
    @abstractmethod
    def load_existing_results(self, original_document_name: str, output_formats: List[str]) -> Optional[Dict[str, str]]:
        """
        Loads existing results for a document if they exist.
        
        :param original_document_name: The name of the original document
        :param output_formats: List of output formats to load
        :return: Dictionary with existing results or None if not found
        """
        pass
    
    @abstractmethod
    def get_documents_to_process(self, output_formats: List[str]) -> List[str]:
        """
        Finds documents that need to be processed (not already in cache).
        
        :param output_formats: List of output formats to check
        :return: List of document paths that need processing
        """
        pass 