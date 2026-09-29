import traceback
from logging import getLogger

from gift_delivery_note_generator.document_parser import DocumentParser
from gift_delivery_note_generator.delivery_note_renderer import DeliveryNoteRenderer

from .services.config import ConfigService


class App:
    def __init__(self) -> None:
        self._logger = getLogger(__name__)

    def run(self) -> None:
        try:
            config_service = ConfigService()
            config = config_service.run()

            document_parser = DocumentParser(config=config)
            delivery_notes = document_parser.run()

            for delivery_note in delivery_notes:
                renderer = DeliveryNoteRenderer(delivery_note=delivery_note, config=config)
                renderer.run()

        except Exception as e:
            self._logger.error(f"An error occurred: {e}")
            traceback.print_exc()
