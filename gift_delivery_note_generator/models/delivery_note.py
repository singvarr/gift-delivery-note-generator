from dataclasses import dataclass
from datetime import date

from gift_delivery_note_generator.models.gift import Gift
from gift_delivery_note_generator.store_config.constants.gift_category import GiftCategory


@dataclass
class GiftEntry:
    recipient: str
    gift: Gift


@dataclass
class DeliveryNote:
    category: GiftCategory
    issue_date: date
    number: int
    gift_store: str
    gifts: list[GiftEntry]
