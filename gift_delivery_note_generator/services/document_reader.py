import os
from pathlib import Path
import shutil

import pytesseract
import pymupdf
from pymupdf import Pixmap
from PIL import Image
import cv2
import numpy as np

from gift_delivery_note_generator.constants.file_names import GIT_KEEP_FILE_NAME
from gift_delivery_note_generator.constants.image_folder import IMAGES_FOLDER

ZOOM = 300 / 72


class DocumentReader:
    """Reads contents of pdf document from file"""
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
            self._remove_blue_stamps_in_image(destination_path)

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
        if item == GIT_KEEP_FILE_NAME:
            continue

        item_path = os.path.join(IMAGES_FOLDER, item)

        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    # TODO: improve it by making more accurate
    def _remove_blue_stamps_in_image(self, image_path: Path) -> None:
        img_bgr = cv2.imread(str(image_path))

        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([90, 40, 40])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=2)

        if cv2.countNonZero(mask) == 0:
            return

        inpainted = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)

        cv2.imwrite(str(image_path), inpainted)

    def run(self) -> str:
        image_paths = self._convert_pdf_to_images()
        result = self._convert_document_to_string(image_paths)
        # self._remove_scanned_images()

        return result
