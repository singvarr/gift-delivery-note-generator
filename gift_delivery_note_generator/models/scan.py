from dataclasses import dataclass

from gift_delivery_note_generator.models.gift import Gift


@dataclass
class ParsedOrderMeta:
    dt: str
    number: str
    # TODO: make it required
    issuer: str = ""


@dataclass
class ParsedDocumentContent:
    meta: ParsedOrderMeta
    gift_entries: list[ScannedGiftEntry]


@dataclass
class ScannedGiftEntry:
    gift: Gift
    full_name: str
    recipient_details: str
