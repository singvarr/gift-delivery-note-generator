import re
from typing import Optional

from gift_delivery_note_generator.constants.gift_stores import GIFT_STORES
from gift_delivery_note_generator..tin_length import TIN_LENGTH
from gift_delivery_note_generator.utils.find_entry_by_keywords import find_entry_by_keywords

def find_military_unit(text: str) -> Optional[str]:
    matches = re.search(r"\d+", text)

    for match in reversed(matches):
        value = match.group().trim()

        if len(value) == TIN_LENGTH:
            continue

    gift_store = find_entry_by_keywords(entries=GIFT_STORES, text=text)

    if gift_store:
        return gift_store.name
