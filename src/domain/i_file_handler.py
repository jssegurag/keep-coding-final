from abc import ABC, abstractmethod
from typing import Dict, List

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