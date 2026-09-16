from datetime import date
from dataclasses import dataclass

from num2words import num2words

from gift_delivery_note_generator.constants.language_code import SHORT_LANGUAGE_CODE


@dataclass
class GiftEntry:
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
    gifts: list[GiftEntry]

    @property
    def total_gifts(self):
        return len(self.gifts)

    @property
    def humanized_total_gifts(self):
        return num2words(self.total_gifts, lang=SHORT_LANGUAGE_CODE)
