import json
import os
from pathlib import Path

from gift_delivery_note_generator.models.gift import Gift
from gift_delivery_note_generator.models.scan import (
    ParsedDocumentContent,
    ParsedOrderMeta,
    ScannedGiftEntry,
)
from gift_delivery_note_generator.store_config.constants.gift_category import GiftCategory


def parse_input_from_json(json_path: str) -> ParsedDocumentContent:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    meta = ParsedOrderMeta(
        dt=data["meta"]["dt"],
        number=data["meta"]["number"],
        issuer=data["meta"].get("issuer", ""),
    )

    gift_entries: list[ScannedGiftEntry] = []

    for unit in data["units"]:
        for entry in unit["gift_entries"]:
            gift_data = entry["gift"]
            category = gift_data.get("category")
            gift = Gift(
                name=gift_data["name"],
                keywords=gift_data.get("keywords") or [],
                category=GiftCategory(category),
            )
            gift_entries.append(
                ScannedGiftEntry(
                    gift=gift,
                    full_name=entry["full_name"],
                    recipient_details=entry["recipient_details"],
                )
            )

    return ParsedDocumentContent(meta=meta, gift_entries=gift_entries)
