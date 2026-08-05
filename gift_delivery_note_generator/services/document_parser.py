import os
from pathlib import Path
import shutil

import pytesseract
import pymupdf
from pymupdf import Pixmap
from PIL import Image

from gift_delivery_note_generator.constants.image_folder import IMAGES_FOLDER

ZOOM = 300 / 72


class DocumentParser:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def _convert_pdf_to_images(self) -> list[Pixmap]:
        image_paths = []

        document = pymupdf.open(self._file_path)
        matrix = pymupdf.Matrix(ZOOM, ZOOM)

        for page_number, page in enumerate(document):
            picture = page.get_pixmap(matrix=matrix)
            destination_path = IMAGES_FOLDER / f"page_{page_number + 1}.png"

            picture.save(destination_path)
            image_paths.append(destination_path)

        return image_paths

    def _convert_document_to_string(self, paths: list[Path]) -> str:
        output = ""

        for path in paths:
            image = Image.open(path)
            output += pytesseract.image_to_string(image, lang='ukr')

        return output

    def _remove_scanned_images(self) -> None:
     for item in os.listdir(IMAGES_FOLDER):
        if item == '.gitkeep':
            continue

        item_path = os.path.join(IMAGES_FOLDER, item)

        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    def run(self) -> str:
        image_paths = self._convert_pdf_to_images()
        result = self._convert_document_to_string(image_paths)
        self._remove_scanned_images()

        return result
