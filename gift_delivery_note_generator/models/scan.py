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
class ParsedOrderMeta:
    dt: str
    number: str


@dataclass
class ParsedDocumentContent:
    meta: ParsedOrderMeta
    gifts: list[ParsedGiftEntry]

@dataclass
class ParsedGiftEntry:
    gift: str
    full_name: str
    recipient_details: str
