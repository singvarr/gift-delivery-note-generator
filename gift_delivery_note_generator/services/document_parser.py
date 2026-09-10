from typing import Optional
from datetime import date
import re

from fuzzy_match import match

from gift_delivery_note_generator.constants.language_code import SHORT_LANGUAGE_CODE
from gift_delivery_note_generator.models.delivery_note import DeliveryNote, GiftEntry
from gift_delivery_note_generator.store_config.constants.gifts import gifts
from gift_delivery_note_generator.store_config.constants.regexps import TIN_NUMBER_REGEXP
from gift_delivery_note_generator.store_config.utils.parse_gift_store import parse_gift_store
from gift_delivery_note_generator.constants.ukrainian_months_in_genitive import (
    UKRAINIAN_MONTHS_IN_GENITIVE,
)
from gift_delivery_note_generator.store_config.utils.build_gift_details_cell import (
    build_gift_details_cell,
)
from gift_delivery_note_generator.models.scan import ParsedDocumentContent
from gift_delivery_note_generator.utils.find_entry_by_keywords import find_entry_by_keywords
import pymorphy3

morph = pymorphy3.MorphAnalyzer(lang=SHORT_LANGUAGE_CODE)


def normalize_word(word: str) -> str:
    parses = morph.parse(word)

    # 1. Шукаємо варіант, який чітко позначений як ім'я, прізвище або по батькові
    for p in parses:
        if any(tag in p.tag for tag in ("Name", "Surn", "Patr")):
            return p.normal_form.capitalize()

    # 2. Якщо це бігаюча голосна / іменник (наприклад, Кравця -> Кравець, Коваля -> Коваль)
    # Звертаємося до першого нормального варіанту
    return parses[0].normal_form.capitalize()


def pib_to_nominative(full_name: str) -> str:
    words = full_name.strip().split()
    result = [normalize_word(w) for w in words]

    if result:
        result[0] = result[0].upper()

    return " ".join(result)


class DocumentParser:
    def __init__(self, contents: ParsedDocumentContent):
        self._contents = contents

    def parse_date_and_order_number(self) -> dict[str, str | None]:
        order_date = self._parse_date_line(self._contents.meta.dt)
        order_number = self._retrieve_number_from_str(self._contents.meta.number)

        return {"date": order_date, "order_number": order_number}

    def _build_delivery_notes(self, issue_date: date, order_issuer: str, order_number: str):
        result = {}

        for entry in self._contents.gift_entries:
            full_name = pib_to_nominative(entry.full_name)
            tin_number = TIN_NUMBER_REGEXP.search(entry.recipient_details)[0]

            recipient_data = f"{full_name} ({tin_number})"
            gift = find_entry_by_keywords(text=entry.gift, entries=gifts)
            store_id = parse_gift_store(text=entry.recipient_details)

            if store_id in result:
                delivery_note = result[store_id]
            else:
                formatted_issue_date = (
                    f"{UKRAINIAN_MONTHS_IN_GENITIVE[issue_date.month - 1]} {issue_date.year}"
                )

                delivery_note = DeliveryNote(
                    issue_date=formatted_issue_date,
                    # TODO: parse it
                    order_date=date.today(),
                    order_issuer=order_issuer,
                    store_id=store_id,
                    order_number=order_number,
                    gifts=[],
                )
                result[store_id] = delivery_note

            order_details = build_gift_details_cell(
                delivery_note=delivery_note,
                gift=gift,
            )

            gift_row = GiftEntry(
                recipient=recipient_data,
                order_details=order_details,
                store_id=store_id,
            )
            delivery_note.gifts.append(gift_row)

        return result

    def run(self):
        order_issuer = "ГК"
        order_number = "1119"

        gifts = self._build_delivery_notes(
            issue_date=date(month=8, day=31, year=2026),
            order_issuer=order_issuer,
            order_number=order_number,
        )

        return list(gifts.values())

    def _parse_date_line(self, date_line: str) -> Optional[str]:
        cleaned = re.sub(r"[a-zA-Zа-яА-ЯіїєґІЇЄҐ]", "", date_line)
        date_line = cleaned.strip("\"'«»")

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
        order_match = re.search(r"\d+", order_line)

        if order_match:
            return order_match.group(0)

        return None
