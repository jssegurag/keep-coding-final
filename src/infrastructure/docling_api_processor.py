import os
from typing import Dict, List
import requests

from src.domain.i_document_processor import IDocumentProcessor
from src.infrastructure.utils import timing_decorator

class DoclingApiProcessor(IDocumentProcessor):
    """
    A concrete implementation of IDocumentProcessor that uses the Docling API
    to process documents.
    """
    def __init__(self, api_base_url: str):
        if not api_base_url:
            raise ValueError("API base URL cannot be empty.")
        self.api_url = f"{api_base_url.rstrip('/')}/v1alpha/convert/file"

    @timing_decorator
    def process(self, file_path: str, output_formats: List[str]) -> Dict[str, str]:
        """
        Sends a document to the Docling API for processing and returns the results.
        """
        results: Dict[str, str] = {}
        
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return results

        files = {'files': (os.path.basename(file_path), open(file_path, 'rb'))}
        # The 'requests' library can handle a list of values for a single key
        # by passing a list of tuples for the 'data' parameter.
        data = [('to_formats', format) for format in output_formats]

        try:
            print(f"Processing {file_path} with formats {output_formats}...")
            response = requests.post(self.api_url, files=files, data=data, timeout=300)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            response_data = response.json()
            
            # Map API response keys to the simple format extension
            for format_ext in output_formats:
                api_key = f"{format_ext}_content"
                if response_data.get("document") and api_key in response_data["document"]:
                    content = response_data["document"][api_key]
                    if content:
                        results[format_ext] = content

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while calling the Docling API: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Ensure the file handle is closed
            if 'files' in locals() and files['files'][1]:
                files['files'][1].close()
        
        return results 