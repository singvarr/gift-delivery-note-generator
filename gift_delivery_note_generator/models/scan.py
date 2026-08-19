from dataclasses import dataclass

from gift_delivery_note_generator.models.gift import Gift

ScannedEntry = tuple[str, str]


@dataclass
class ScannedSection:
    gift_name: str
    entries: list[ScannedEntry]


@dataclass
class ScannedTextToken:
    page: int
    left: int
    top: int
    width: int
    height: int
    text: str


ScannedLine = list[ScannedTextToken]


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
