from dataclasses import dataclass

from gift_delivery_note_generator.constants.gift_category import GiftCategory
from gift_delivery_note_generator.models.entry import Entry


@dataclass
class Gift(Entry):
    category: GiftCategory
