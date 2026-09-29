from dataclasses import dataclass

from ..settings.models.gift_category import GiftCategory
from .entry import Entry


@dataclass(kw_only=True)
class Gift(Entry):
    category: GiftCategory
    priority: int = 0
