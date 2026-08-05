from typing import Optional
from dataclasses import dataclass

from gift_delivery_note_generator.models.entry import Entry


@dataclass
class GiftStore(Entry):
    internal_id: Optional[str] = None
