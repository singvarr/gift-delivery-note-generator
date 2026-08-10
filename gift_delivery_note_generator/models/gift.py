from dataclasses import dataclass

from gift_delivery_note_generator.store_config.constants.gift_category import GiftCategory
from gift_delivery_note_generator.models.entry import Entry


@dataclass(kw_only=True)
class Gift(Entry):
    category: GiftCategory
