import os
from pathlib import Path
import shutil

import pytesseract
import pymupdf
from PIL import Image

# OpenCV is used to detect and remove blue stamps from scanned images.
# Only install cv2 as a new dependency as requested. Numpy is required by OpenCV and
# is expected to be available alongside it.
import cv2
import numpy as np

from gift_delivery_note_generator.constants.image_folder import IMAGES_FOLDER

ZOOM = 300 / 72


class DocumentParser:
    def __init__(self, file_path: Path):
        self._file_path = file_path

    def _convert_pdf_to_images(self) -> list[Path]:
        image_paths = []

        document = pymupdf.open(self._file_path)
        matrix = pymupdf.Matrix(ZOOM, ZOOM)

        for page_number, page in enumerate(document):
            picture = page.get_pixmap(matrix=matrix)
            destination_path = IMAGES_FOLDER / f"page_{page_number + 1}.png"

            picture.save(destination_path)

            # Attempt to remove blue stamps right after saving the page image.
            try:
                self._remove_blue_stamps_in_image(destination_path)
            except Exception:
                # If OpenCV processing fails for any reason, keep the original image
                # so OCR still proceeds.
                pass

            image_paths.append(destination_path)

        return image_paths

    def _convert_document_to_string(self, paths: list[Path]) -> str:
        output = ""

        for path in paths:
            image = Image.open(path)
            output += pytesseract.image_to_string(image, lang='ukr')

        return output

    def _remove_blue_stamps_in_image(self, image_path: Path) -> None:
        """
        Detect visually-blue regions (common stamp color) and inpaint them.

        Approach:
        - Read image with OpenCV (BGR).
        - Convert to HSV and threshold a broad blue range.
        - Clean the mask with morphological operations to remove noise.
        - Use inpainting to replace masked regions with surrounding content.

        This will assume cv2 and numpy are installed; processing errors are
        handled by the caller.
        """

        img_bgr = cv2.imread(str(image_path))
        if img_bgr is None:
            return

        # Convert to HSV to threshold blue colors. These ranges are intentionally
        # broad to capture typical blue stamp inks found on scanned documents.
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # Blue-ish ranges: tune if you have sample images. Hue range roughly 90-140.
        lower_blue = np.array([90, 40, 40])
        upper_blue = np.array([140, 255, 255])
        mask =  (hsv, lower_blue, upper_blue)

        # Morphological operations to remove small noise and fill small holes.
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=2)

        # If the mask is empty (no blue detected), skip to avoid accidental changes.
        if cv2.countNonZero(mask) == 0:
            return

        # Inpaint using the Telea algorithm. Radius can be adjusted if needed.
        inpainted = cv2.inpaint(img_bgr, mask, 3, cv2.INPAINT_TELEA)

        # Overwrite the original image file with the cleaned version.
        cv2.imwrite(str(image_path), inpainted)

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
