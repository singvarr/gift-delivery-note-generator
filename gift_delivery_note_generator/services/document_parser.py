from typing import Optional
from pathlib import Path
import re

from fuzzy_match import match

from gift_delivery_note_generator.store_config.constants.gifts import gifts
from gift_delivery_note_generator.store_config.constants.regexps import TIN_NUMBER_REGEXP
from gift_delivery_note_generator.store_config.utils.parse_gift_store import parse_gift_store
from gift_delivery_note_generator.constants.months import UKRAINIAN_MONTHS_IN_GENITIVE
from gift_delivery_note_generator.models.scan import ParsedDocumentContent
from gift_delivery_note_generator.utils.find_entry_by_keywords import find_entry_by_keywords

class DocumentParser:
    def __init__(self, contents: ParsedDocumentContent):
        self._contents = contents

    def parse_date_and_order_number(self) -> dict[str, str | None]:
        order_header = self._extract_order_header()

        city_match = re.search(r"\bм\s*\.\s*київ\b", order_header, re.IGNORECASE)

        if not city_match:
            return {"date": None, "order_number": None}

        prefix = order_header[: city_match.start()]

        date_line = self._last_non_empty_line(prefix)
        order_date = self._parse_date_line(date_line)

        suffix = order_header[city_match.end() :]

        order_line = self._get_first_non_empty_line(suffix)
        order_number = self._retrieve_number_from_str(order_line)

        return {"date": order_date, "order_number": order_number}

    def _parse_gifts(self):
        result = []

        for entry in self._contents.gifts:
            gift_name = find_entry_by_keywords(text=entry.gift, entries=gifts)
            # full_name =
            tin_number = TIN_NUMBER_REGEXP.match(entry.recipient_details)[0]
            gift_store = parse_gift_store(text=entry.recipient_details)

    def run(self):
        gifts = self._parse_gifts()

        print(gifts)

    def _extract_order_header(self) -> str:
        start_match = re.search(
            r"витяг\s+(?:із|з)\s+наказу", self._contents, re.IGNORECASE
        )

        if not start_match:
            raise Exception(
                "Failed to find the start of the order header in the scanned document"
            )

        start_index = start_match.end()
        remaining_text = self._contents[start_index:]
        end_match = re.search(r"наказую\s*:?", remaining_text, re.IGNORECASE)

        if not end_match:
            raise Exception("Failed to find the end of the order header in the scanned document")

        end_index = start_index + end_match.start()

        return self._contents[start_index:end_index]

    def _get_first_non_empty_line(self, text: str) -> str:
        lines = text.splitlines()
        for line in lines:
            candidate = line.strip()
            if candidate:
                return candidate
        return ""

    def _last_non_empty_line(self, text: str) -> str:
        lines = text.splitlines()

        for line in reversed(lines):
            candidate = line.strip()
            if candidate:
                return candidate
        return ""

    def _parse_date_line(self, date_line: str) -> Optional[str]:
        date_line = date_line.strip("\"'«»")

        parts = date_line.split()

        if len(parts) < 3:
            return None

        day = parts[0][:2]
        month_match = match.extractOne(parts[1].lower(), UKRAINIAN_MONTHS_IN_GENITIVE)
        year = parts[2]

        month = month_match[0] if month_match else "-"

        return f"{day} {month} {year}"

    # TODO: add fucking predicate for convenient parsing of this shit without extra regexp
    def _retrieve_number_from_str(self, order_line: str) -> Optional[str]:
        # TODO: compile this fuckery
        order_match = re.search(r'\d+', order_line)

        if order_match:
            return order_match.group(0)

        return None
