from abc import ABC, abstractmethod
from typing import Dict, List

class IDocumentProcessor(ABC):
    """
    Defines the contract for a document processor.
    """

    @abstractmethod
    def process(self, file_path: str, output_formats: List[str]) -> Dict[str, str]:
        """
        Processes a single document and returns its content in various formats.

        :param file_path: The absolute path to the document file.
        :param output_formats: A list of desired output formats (e.g., ['md', 'json']).
        :return: A dictionary where keys are the format and values are the
                 processed content.
        """
        pass 