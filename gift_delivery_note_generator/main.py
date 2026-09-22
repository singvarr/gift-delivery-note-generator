import os
import traceback

from dotenv import load_dotenv

from gift_delivery_note_generator.services.document_parser import DocumentParser
from gift_delivery_note_generator.services.delivery_note_renderer import DeliveryNoteRenderer
from gift_delivery_note_generator.utils.parse_input_from_json import parse_input_from_json

if __name__ == "__main__":
    load_dotenv()

    try:
        if "PARSED_ORDER_JSON_PATH" not in os.environ:
            raise Exception("JSON with order data is not provided")

        json_path = os.environ["PARSED_ORDER_JSON_PATH"]
        scanned_document = parse_input_from_json(json_path)

        document_parser = DocumentParser(contents=scanned_document)
        parsed_data = document_parser.run()

        for delivery_note in parsed_data:
            renderer = DeliveryNoteRenderer(delivery_note=delivery_note)
            renderer.run()

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
