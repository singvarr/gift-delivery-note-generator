from typing import Optional
from dataclasses import dataclass

from .entry import Entry


@dataclass
class GiftStore(Entry):
    internal_id: Optional[str] = None
    search_phrase: str = ""
