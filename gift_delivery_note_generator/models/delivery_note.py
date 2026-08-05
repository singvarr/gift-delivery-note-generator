from dataclasses import dataclass
from datetime import date

from gift_delivery_note_generator.models.gift import Gift


@dataclass
class GiftEntry:
    recipient: str
    gift: Gift


@dataclass
class DeliveryNote:
    issue_date: date
    gift_store: str
    gifts: list[GiftEntry]
