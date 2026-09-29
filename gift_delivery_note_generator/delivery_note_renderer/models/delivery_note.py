from datetime import date
from dataclasses import dataclass

from num2words import num2words

from gift_delivery_note_generator.app.constants.language_code import LANGUAGE_CODE


@dataclass
class DeliveryNoteEntry:
    recipient: str
    order_details: str
    store_id: str


@dataclass
class DeliveryNote:
    issue_date: date
    order_issuer: str
    order_date: date
    order_number: str
    store_id: str
    gifts: list[DeliveryNoteEntry]

    @property
    def total_gifts(self):
        return len(self.gifts)

    @property
    def humanized_total_gifts(self):
        return num2words(self.total_gifts, lang=LANGUAGE_CODE)
