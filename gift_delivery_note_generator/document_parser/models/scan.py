from dataclasses import dataclass

from .gift import Gift


@dataclass
class ParsedOrderMeta:
    dt: str
    number: str
    # TODO: make it required
    issuer: str = ""


@dataclass
class GiftEntryGroup:
    store_name: str
    entries: list[ScannedGiftEntry]


@dataclass
class ParsedDocumentContent:
    meta: ParsedOrderMeta
    gift_entries: list[GiftEntryGroup]


@dataclass
class ScannedGiftEntry:
    gift: Gift
    full_name: str
    recipient_details: str
