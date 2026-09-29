from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pymorphy3 import MorphAnalyzer

from gift_delivery_note_generator.app.constants.language_code import LANGUAGE_CODE
from gift_delivery_note_generator.delivery_note_renderer import DeliveryNote, DeliveryNoteEntry
from gift_delivery_note_generator.document_parser.settings.utils.parse_gift_store import (
    parse_gift_store,
)

from ..constants.tin_number_regexp import TIN_NUMBER_REGEXP
from ..constants.ukrainian_months_in_genitive import UKRAINIAN_MONTHS_IN_GENITIVE
from ..settings.utils.build_gift_details_cell import build_gift_details_cell
from ..settings.utils.get_order_issuer import get_order_issuer

if TYPE_CHECKING:
    from gift_delivery_note_generator.app import Config


class DocumentParser:
    def __init__(self, config: Config):
        self._config = config
        self._morph = MorphAnalyzer(lang=LANGUAGE_CODE)

    def _convert_word_to_nominative(self, word: str) -> str:
        parses = self._morph.parse(word)

        for p in parses:
            if any(tag in p.tag for tag in ("Name", "Surn", "Patr")):
                return p.normal_form.capitalize()

        return parses[0].normal_form.capitalize()

    def _convert_full_name_to_nominative(self, full_name: str) -> str:
        words = full_name.strip().split()
        result = [self._convert_word_to_nominative(w) for w in words]

        if result:
            result[0] = result[0].upper()

        return " ".join(result)

    def _parse_order_date(self) -> date:
        day_str, month_str, year_str, _ = self._config.order.meta.dt.split(" ")
        month = next(i + 1 for i, m in enumerate(UKRAINIAN_MONTHS_IN_GENITIVE) if m == month_str)

        return date(year=int(year_str), month=month, day=int(day_str))

    def _build_delivery_notes(self, order_issuer: str) -> dict[str, DeliveryNote]:
        result = {}

        order_date = self._parse_order_date()

        for group in self._config.order.gift_entries:
            for entry in group.entries:
                full_name = self._convert_full_name_to_nominative(entry.full_name)

                tin_match = TIN_NUMBER_REGEXP.search(entry.recipient_details)

                if tin_match:
                    tin_number = tin_match.group(0)
                    recipient_data = f"{full_name} ({tin_number})"
                else:
                    recipient_data = full_name

                store_id = parse_gift_store(
                    text=entry.recipient_details,
                    gift_stores=self._config.gift_stores,
                )

                if store_id in result:
                    delivery_note = result[store_id]
                else:
                    issue_date = date.today()
                    formatted_issue_date = (
                        f"{UKRAINIAN_MONTHS_IN_GENITIVE[issue_date.month - 1]} {issue_date.year}"
                    )

                    delivery_note = DeliveryNote(
                        order_date=order_date,
                        issue_date=formatted_issue_date,
                        order_issuer=order_issuer,
                        store_id=store_id,
                        order_number=self._config.order.meta.number,
                        gifts=[],
                    )
                    result[store_id] = delivery_note

                order_details = build_gift_details_cell(
                    delivery_note=delivery_note,
                    gift=entry.gift,
                )

                gift_row = DeliveryNoteEntry(
                    recipient=recipient_data,
                    order_details=order_details,
                    store_id=store_id,
                )
                delivery_note.gifts.append(gift_row)

        return result

    def run(self):
        order_issuer = get_order_issuer()

        gifts = self._build_delivery_notes(order_issuer=order_issuer)

        return list(gifts.values())
