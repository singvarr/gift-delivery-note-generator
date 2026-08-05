import os
from pathlib import Path

from dotenv import load_dotenv

from gift_delivery_note_generator.services.document_parser import DocumentParser

if __name__ == "__main__":
    load_dotenv()

    try:
        sample_path = Path(os.environ["SAMPLE_PDF_PATH"])

        document_scanner = DocumentParser(file_path=sample_path)
        document_scanner.run()
    except Exception as e:
        print(f"An error occurred: {e}")