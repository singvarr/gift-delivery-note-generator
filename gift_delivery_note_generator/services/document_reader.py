import os
import re
from pathlib import Path
from csv import DictReader
from io import BytesIO, StringIO
from statistics import mean
from typing import Iterable
import shutil

from rapidfuzz import fuzz
import pytesseract
import pymupdf
from PIL import Image

from gift_delivery_note_generator.constants.ocr_misread_numbers import OCR_MISREAD_NUMBERS_MAPPINGS
from gift_delivery_note_generator.store_config.constants.error_messages import ErrorMessages
from gift_delivery_note_generator.constants.file_names import GIT_KEEP_FILE_NAME
from gift_delivery_note_generator.constants.paths import IMAGES_FOLDER
from gift_delivery_note_generator.constants.scan_settings import (
    MIN_CONFIDENCE_THRESHOLD_PERCENTAGE,
    SCANNED_WORD_LEVEL,
    Y_AXIS_JITTER_TOLERANCE_IN_PX,
    ZOOM,
)
from gift_delivery_note_generator.store_config.utils.get_ocr_match_rules import get_ocr_match_config
from gift_delivery_note_generator.store_config.constants.order_details_anchor import (
    ORDER_DETAILS_ANCHOR,
)
from gift_delivery_note_generator.store_config.constants.regexps import (
    GIFT_ENTRY_NUMBER_REGEX,
    RECIPIENT_INFO_REGEXP,
)
from gift_delivery_note_generator.models.scan import (
    ParsedOrderMeta,
    ParsedDocumentContent,
    ScannedGiftEntry,
    ScannedLine,
    ScannedTextToken,
)


class DocumentReader:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    @staticmethod
    def _join_text_tokens(tokens: Iterable[ScannedTextToken]) -> str:
        return " ".join(token.text for token in tokens)

    def _convert_pdf_to_images(self):
        image_paths = []

        document = pymupdf.open(self._file_path)
        matrix = pymupdf.Matrix(ZOOM, ZOOM)

        index = 1

        for page in document:
            pixmap = page.get_pixmap(matrix=matrix)
            image_bytes = BytesIO(pixmap.tobytes("png"))

            with Image.open(image_bytes) as img:
                width, height = img.size

                midpoint = width // 2

                left_page = img.crop((0, 0, midpoint, height))
                left_page_destination_path = IMAGES_FOLDER / f"page_{index}.png"
                left_page.save(left_page_destination_path)
                image_paths.append(left_page_destination_path)
                index += 1

                right_page = img.crop((midpoint, 0, width, height))
                right_page_destination_path = IMAGES_FOLDER / f"page_{index}.png"
                right_page.save(right_page_destination_path)
                image_paths.append(right_page_destination_path)
                index += 1

        return image_paths

    def _split_document(
        self, tokens: list[ScannedTextToken]
    ) -> tuple[list[ScannedTextToken], list[ScannedTextToken]]:
        pass

    def _parse_and_group_text_by_lines(
        self,
        tokens: list[ScannedTextToken],
        y_axis_jitter_tolerance: int,
    ) -> ScannedLine:
        if not tokens:
            raise Exception(ErrorMessages.NO_CONTENT_IN_DOCUMENT)

        tokens.sort(key=lambda token: (token.page, token.top, token.left))

        lines = []
        current_line = [tokens[0]]
        line_counter = 1

        for entry in tokens[1:]:
            avg_top = mean(line_entry.top for line_entry in current_line)

            if abs(entry.top - avg_top) <= y_axis_jitter_tolerance:
                current_line.append(entry)
            else:
                current_line.sort(key=lambda entry: entry.left)
                lines.append(current_line)

                line_counter += 1
                current_line = [entry]

        if current_line:
            current_line.sort(key=lambda entry: entry.left)
            lines.append(current_line)

        return lines

    def _extract_order_details(self, lines: list[ScannedLine]):
        for line in lines:
            for index, token in enumerate(line):
                if ORDER_DETAILS_ANCHOR.lower() in token.text.strip().lower():
                    order_date = DocumentReader._join_text_tokens(line[:index])
                    order_number = DocumentReader._join_text_tokens(line[index + 1 :])

                    return ParsedOrderMeta(dt=order_date, number=order_number)

        raise Exception(ErrorMessages.FAILED_TO_PARSE_ORDER_HEADER)

    def _group_content(self, lines: list[ScannedLine]) -> ParsedDocumentContent:
        meta = self._extract_order_details(lines=lines)
        gifts = self._extract_sections(lines=lines)

        return ParsedDocumentContent(meta=meta, gift_entries=gifts)

    def _clean_last_section(self, lines: list[ScannedLine]) -> list[ScannedLine]:
        for index, line in enumerate(reversed(lines)):
            line_text = DocumentReader._join_text_tokens(tokens=line)

            if RECIPIENT_INFO_REGEXP.search(line_text.lower()):
                return lines[: index * -1]

        return lines

    def _structure_entry_contents(self, gift: str, entry: list[ScannedLine]) -> ScannedGiftEntry:
        full_name = ""
        recipient_details = ""

        for index, line in enumerate(entry):
            if index == 0:
                full_name += line[1].text
                recipient_details += DocumentReader._join_text_tokens(line[2:])

                left_boundary = line[2].left
            else:
                for token in line:
                    if token.left >= left_boundary - Y_AXIS_JITTER_TOLERANCE_IN_PX:
                        recipient_details += " " + token.text
                    else:
                        full_name += " " + token.text

        recipient_details = self._fix_ocr_integers_with_known_candidates(recipient_details)

        return ScannedGiftEntry(gift=gift, full_name=full_name, recipient_details=recipient_details)

    def _parse_gift_group(self, section: list[ScannedLine]):
        stop_index = next(
            index
            for index, line in enumerate(section)
            if GIFT_ENTRY_NUMBER_REGEX.match(line[0].text)
        )

        gift_name_entries = sum(section[:stop_index], [])
        gift_text = " ".join(entry.text for entry in gift_name_entries)

        breakpoints = []

        for index, line in enumerate(section):
            if GIFT_ENTRY_NUMBER_REGEX.match(line[0].text) and (
                index == stop_index
                or RECIPIENT_INFO_REGEXP.search(
                    DocumentReader._join_text_tokens(section[index - 1])
                )
            ):
                breakpoints.append(index)

        unstructured_sections = []

        for index, breakpoint in enumerate(breakpoints):
            is_last_section = index == len(breakpoints) - 1

            if is_last_section:
                gift_entry = section[breakpoint:]
            else:
                gift_entry = section[breakpoint : breakpoints[index + 1]]

            unstructured_sections.append(gift_entry)

        structured_entries = []

        for unstructured_section in unstructured_sections:
            structured_gift_entry = self._structure_entry_contents(
                gift=gift_text,
                entry=unstructured_section,
            )
            structured_entries.append(structured_gift_entry)

        return structured_entries

    def _extract_sections(self, lines: list[ScannedLine]):
        group_breakpoints = []

        for index, line in enumerate(lines):
            if line[0].text.lower().startswith("нагородити"):
                group_breakpoints.append(index)

        gift_groups = []

        for index, breakpoint in enumerate(group_breakpoints):
            is_last_group = index == len(group_breakpoints) - 1

            if is_last_group:
                section_lines = lines[breakpoint:]
                gift_group = self._clean_last_section(lines=section_lines)
            else:
                gift_group = lines[breakpoint : group_breakpoints[index + 1]]

            gift_groups.append(gift_group)

        parsed_gift_groups = []

        for gift_group in gift_groups:
            parsed_gift_groups.append(self._parse_gift_group(gift_group))

        return [item for group in parsed_gift_groups for item in group]

    def _parse_text_tokens_from_images(self, paths: list[Path]) -> list[ScannedTextToken]:
        result = []

        for page_idx, path in enumerate(paths):
            with Image.open(path) as img:
                raw_tsv = pytesseract.image_to_data(img, lang="ukr")

                cleaned_string = raw_tsv.strip("'\n ")

                f = StringIO(cleaned_string)
                reader = DictReader(f, delimiter="\t")

                for row in reader:
                    should_omit = (
                        row["text"] is None
                        or isinstance(row["text"], str)
                        and row["text"].strip() == "-"
                    )

                    if (
                        int(row["level"]) == SCANNED_WORD_LEVEL
                        and float(row["conf"]) >= MIN_CONFIDENCE_THRESHOLD_PERCENTAGE
                        and not should_omit
                    ):
                        token = ScannedTextToken(
                            page=page_idx,
                            left=int(row["left"]),
                            top=int(row["top"]),
                            width=int(row["width"]),
                            height=int(row["height"]),
                            text=row["text"].strip(),
                        )
                        result.append(token)

        return result

    def _fix_ocr_integers_with_known_candidates(self, text: str, score_cutoff: float = 70.0) -> str:
        anchor_rules = get_ocr_match_config()
        current_text = text

        for anchor_phrase, candidates in anchor_rules.items():
            anchor_len = len(anchor_phrase)
            search_start = 0

            while search_start < len(current_text):
                best_score = 0.0
                best_start_idx = -1
                best_window_len = anchor_len

                # Сканування тексту на наявність якоря
                text_to_search = current_text[search_start:]
                text_len = len(text_to_search)

                for window_len in range(max(1, anchor_len - 2), anchor_len + 3):
                    for i in range(text_len - window_len + 1):
                        window = text_to_search[i : i + window_len]
                        score = fuzz.ratio(anchor_phrase.lower(), window.lower())

                        if score > best_score and score >= score_cutoff:
                            best_score = score
                            best_start_idx = search_start + i
                            best_window_len = window_len

                if best_start_idx == -1:
                    break

                # Визначення токена (слова) безпосередньо перед якорем
                prefix = current_text[:best_start_idx].rstrip()

                if prefix:
                    last_space_idx = prefix.rfind(" ")
                    if last_space_idx == -1:
                        raw_num_token = prefix
                        token_start_idx = 0
                    else:
                        raw_num_token = prefix[last_space_idx + 1 :]
                        token_start_idx = last_space_idx + 1

                    # КРОК А: Нормалізація токена через ocr_to_digits
                    normalized_token = "".join(
                        OCR_MISREAD_NUMBERS_MAPPINGS.get(char, char) for char in raw_num_token
                    )
                    normalized_token = re.sub(r"\D", "", normalized_token)  # Залишаємо лише цифри

                    matched_candidate = None

                    # КРОК Б: Точний або Fuzzy підбір серед дозволеного списку кандидатів
                    if normalized_token in candidates:
                        matched_candidate = normalized_token
                    else:
                        # Якщо навіть після нормалізації число не ідеальне, шукаємо найближчого кандидата
                        best_cand_score = -1.0
                        for cand in candidates:
                            # Порівнюємо як сирий токен, так і нормалізований з кандидатом
                            cand_score = max(
                                fuzz.ratio(normalized_token, cand),
                                fuzz.ratio(raw_num_token.lower(), cand.lower()),
                            )
                            if cand_score > best_cand_score:
                                best_cand_score = cand_score
                                matched_candidate = cand

                    # КРОК В: Заміна зіпсованого токена на відновий кандидат
                    if matched_candidate:
                        token_end_idx = token_start_idx + len(raw_num_token)
                        current_text = (
                            current_text[:token_start_idx]
                            + matched_candidate
                            + current_text[token_end_idx:]
                        )
                        diff = len(matched_candidate) - len(raw_num_token)
                        best_start_idx += diff

                search_start = best_start_idx + best_window_len

        return current_text

    def _remove_scanned_images(self) -> None:
        for item in os.listdir(IMAGES_FOLDER):
            if item == GIT_KEEP_FILE_NAME:
                continue

        item_path = os.path.join(IMAGES_FOLDER, item)

        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    def run(self) -> ParsedDocumentContent:
        # Step 1. Convert pdf to png
        image_paths = self._convert_pdf_to_images()
        # Step 2. Read image contents
        tokens = self._parse_text_tokens_from_images(paths=image_paths)
        # Step 3. Perform OCR and break group scanned text in lines
        lines = self._parse_and_group_text_by_lines(
            tokens=tokens,
            y_axis_jitter_tolerance=Y_AXIS_JITTER_TOLERANCE_IN_PX,
        )
        # Step 4. Group content logically and extract section with information from lines
        result = self._group_content(lines=lines)
        # Step 5. Remove processed png files
        # self._remove_scanned_images()

        return result
