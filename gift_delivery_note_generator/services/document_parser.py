import re
from pathlib import Path
from typing import Optional

from fuzzy_match import match


from gift_delivery_note_generator.constants.image_folder import IMAGES_FOLDER
from gift_delivery_note_generator.constants.months import UKRAINIAN_MONTHS_IN_GENITIVE

ZOOM = 300 / 72


class DocumentParser:
    def __init__(self, contents: Path):
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
        order_number = self._parse_order_number(order_line)

        return {"date": order_date, "order_number": order_number}

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
        month = match.extractOne(parts[1].lower(), UKRAINIAN_MONTHS_IN_GENITIVE)
        year = parts[2]

        return f"{day} {month} {year}"

    def _parse_order_number(self, order_line: str) -> str | None:
        order_match = re.search(
            r"\b(?:м\s*|номер\s*|№\s*)?\s*(\d{1,7})\b", order_line, re.IGNORECASE
        )
        if not order_match:
            return None

        return order_match.group(1)