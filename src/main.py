import os
from dotenv import load_dotenv

from src.infrastructure.docling_api_processor import DoclingApiProcessor
from src.infrastructure.local_file_handler import LocalFileHandler
from src.application.process_documents_use_case import ProcessDocumentsUseCase

def main():
    """
    Main function to initialize and run the document processing application.
    """
    # Load environment variables from a .env file
    load_dotenv()
    api_base_url = os.getenv("API_BASE_URL")
    try:
        max_workers = int(os.getenv("MAX_WORKERS", "10"))
    except (ValueError, TypeError):
        print("Warning: MAX_WORKERS is not a valid number. Using default (10).")
        max_workers = 10


    if not api_base_url:
        print("Error: API_BASE_URL is not set. Please create a .env file with the API URL.")
        print("Example: API_BASE_URL=http://localhost:8000")
        return

    # 1. Define the desired output formats
    # According to openapi.json: md, json, html, html_split_page, text, doctags
    output_formats_to_generate = [ "json"]

    # 2. Instantiate concrete implementations (Infrastructure layer)
    file_handler = LocalFileHandler(source_dir='src/resources/docs', target_dir='target')
    document_processor = DoclingApiProcessor(api_base_url=api_base_url)

    # 3. Instantiate the use case and inject dependencies (Application layer)
    process_documents_use_case = ProcessDocumentsUseCase(
        document_processor=document_processor,
        file_handler=file_handler,
        max_workers=max_workers
    )

    # 4. Execute the use case
    process_documents_use_case.execute(output_formats=output_formats_to_generate)


if __name__ == "__main__":
    main() 