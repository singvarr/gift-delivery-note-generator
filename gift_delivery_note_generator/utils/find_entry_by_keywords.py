from typing import Iterable, Optional

from gift_delivery_note_generator.models.entry import Entry


def find_entry_by_keywords(text: str, entries: Iterable[Entry]) -> Optional[Entry]:
    return next(
        (
            entry
            for entry in entries
            if all(keyword in text for keyword in entry.keywords)
        ),
        None,
    )
