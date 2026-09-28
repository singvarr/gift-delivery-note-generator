from dataclasses import dataclass
from pathlib import Path

from gift_delivery_note_generator.models.gift import Gift
from gift_delivery_note_generator.models.gift_store import GiftStore
from gift_delivery_note_generator.models.scan import ParsedDocumentContent


@dataclass
class Config:
    template_path: Path
    output_path: Path
    gifts: list[Gift]
    gift_stores: list[GiftStore]
    order: ParsedDocumentContent
