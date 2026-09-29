from dataclasses import dataclass

from .gift import Gift


@dataclass
class OrderMeta:
    dt: str
    number: str
    issuer: str


@dataclass
class OrderRecord:
    gift: Gift
    full_name: str
    recipient_details: str


@dataclass
class OrderRecordsGroup:
    store_name: str
    entries: list[OrderRecord]


@dataclass
class Order:
    meta: OrderMeta
    gift_entries: list[OrderRecordsGroup]
