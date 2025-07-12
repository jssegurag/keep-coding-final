import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.domain.i_document_processor import IDocumentProcessor
from src.domain.i_file_handler import IFileHandler

class ProcessDocumentsUseCase:
    """
    This use case orchestrates the document processing workflow.
    It relies on abstractions (interfaces) for decoupling and testability.
    """
    def __init__(self, document_processor: IDocumentProcessor, file_handler: IFileHandler, max_workers: int = 10):
        self.document_processor = document_processor
        self.file_handler = file_handler
        self.max_workers = max_workers

    def _process_single_document(self, doc_path: str, output_formats: list[str]):
        """Helper method to process one document and save the result."""
        try:
            print(f"Submitting {os.path.basename(doc_path)} for processing...")
            processed_content = self.document_processor.process(doc_path, output_formats)
            if processed_content:
                original_name = os.path.basename(doc_path)
                self.file_handler.save_results(original_name, processed_content)
                return f"Successfully processed {original_name}"
            else:
                return f"No content was returned for {os.path.basename(doc_path)}"
        except Exception as e:
            return f"Failed to process document {os.path.basename(doc_path)}: {e}"

    def execute(self, output_formats: list[str]):
        """
        Executes the use case: finds documents, processes them concurrently,
        and saves the results.
        """
        print("Starting document processing workflow...")
        documents_to_process = self.file_handler.find_documents()

        if not documents_to_process:
            print("No documents found to process.")
            return

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            print(f"Processing {len(documents_to_process)} documents with up to {self.max_workers} threads...")
            
            future_to_doc = {
                executor.submit(self._process_single_document, doc, output_formats): doc
                for doc in documents_to_process
            }

            for future in as_completed(future_to_doc):
                doc_path = future_to_doc[future]
                try:
                    result_message = future.result()
                    print(result_message)
                except Exception as exc:
                    print(f"{os.path.basename(doc_path)} generated an exception: {exc}")

        print("-" * 20)
        print("Document processing workflow finished.") 