import os
from pathlib import Path

from dotenv import load_dotenv

from gift_delivery_note_generator.services.document_parser import DocumentParser
from gift_delivery_note_generator.services.document_reader import DocumentReader
from gift_delivery_note_generator.services.delivery_note_renderer import DeliveryNoteRenderer


if __name__ == "__main__":
    load_dotenv()

    try:
        sample_path = Path(os.environ["SAMPLE_PDF_PATH"])

        document_reader = DocumentReader(file_path=sample_path)
        scanned_document = document_reader.run()
        document_parser = DocumentParser(contents=scanned_document)
        parsed_data = document_parser.run()

        for delivery_note in parsed_data:
            renderer = DeliveryNoteRenderer(delivery_note=delivery_note)
            renderer.run()

    except Exception as e:
        print(f"An error occurred: {e}")
