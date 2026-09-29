from typing import Iterable, Optional

from ...entry import Entry


def find_entry_by_keywords(text: str, entries: Iterable[Entry]) -> Optional[Entry]:
    return next(
        (entry for entry in entries if all(keyword in text.lower() for keyword in entry.keywords)),
        None,
    )
