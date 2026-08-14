from dataclasses import dataclass

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
class ParsedDocumentContent:
    order_date: str
    order_number: str
    gifts: list[ParsedGiftEntry]


@dataclass
class ParsedGiftEntry:
    gift: str
    full_name: str
    recipient_details: str
