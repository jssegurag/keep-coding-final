import os
from typing import Dict, List
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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

    @retry(
        stop=stop_after_attempt(2),  # Un reintento (2 intentos total)
        wait=wait_exponential(multiplier=1, min=4, max=10),  # Espera exponencial entre 4-10 segundos
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
        reraise=True
    )
    @timing_decorator
    def _make_api_call(self, files: Dict, data: List) -> requests.Response:
        """
        Realiza la llamada a la API con reintentos automáticos.
        """
        print(f"Realizando llamada a la API: {self.api_url}")
        response = requests.post(self.api_url, files=files, data=data, timeout=300)
        response.raise_for_status()
        return response

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
            
            # Usar el método con reintentos
            response = self._make_api_call(files, data)
            response_data = response.json()
            
            # Map API response keys to the simple format extension
            for format_ext in output_formats:
                api_key = f"{format_ext}_content"
                if response_data.get("document") and api_key in response_data["document"]:
                    content = response_data["document"][api_key]
                    if content:
                        results[format_ext] = content

        except requests.exceptions.RequestException as e:
            print(f"Error en la llamada a la API Docling después de reintentos: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Ensure the file handle is closed
            if 'files' in locals() and files['files'][1]:
                files['files'][1].close()
        
        return results 