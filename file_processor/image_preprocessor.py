import math

import cv2
import numpy as np
import pytesseract

from config import config
from config.config import SUPPORTED_LANGUAGES
from utils import run_sync_fn_async, filter_for_lang_detection
from .filters import generic_filter
from .metadata import determine_text_language


# gray-scaling
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def blur(image):
    return cv2.GaussianBlur(image, (3, 3), 0)


# binarization
def thresholding(image):
    return cv2.adaptiveThreshold(image, 255,
                                 cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 5)


# morphology
def morpho(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


def deskew_image(
        image: np.ndarray, angle: float, background
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)


async def find_best_rotation(preprocessed_image):
    """
    Find the best among 4 possible rotations of the image based on the average confidence of the text recognition by easyocr
    :param preprocessed_image: image after preprocessing
    :return: rotated image, text returned by tesseract, language of the text, confidence of the language
    """
    best_confidence = -np.inf
    best_rotation = preprocessed_image
    best_text = ""
    lang = None
    best_lang_confidence = 0

    angle_to_cv2 = {
        90: cv2.ROTATE_90_COUNTERCLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_CLOCKWISE,
    }

    for angle in [0, 90, 180, 270]:
        rotated = cv2.rotate(preprocessed_image, angle_to_cv2[angle]) if angle != 0 else preprocessed_image

        # Extract the detection confidences of current orientation but exclude empty, or non-alphanumeric text
        data = await run_sync_fn_async(pytesseract.image_to_data, rotated, lang=config.TESSERACT_LANG_STRING,
                                       output_type=pytesseract.Output.DICT)

        confidences = []
        text = ""
        # Extract the detection confidences of current orientation but exclude empty, or non-alphanumeric text
        for detected_text, conf in zip(data["text"], data["conf"]):
            if not detected_text.isspace() and conf != -1:
                confidences.append(conf)
                text += detected_text + " "

        if not confidences:
            continue

        detection_confidence = sum(confidences) / len(confidences)
        text = generic_filter(text)
        text = text.lower()

        # filter out non-alphanumeric characters for language detection
        filtered_text = filter_for_lang_detection(text)

        lang, lang_confidence = determine_text_language(filtered_text, ocr=True)
        if not lang or lang not in SUPPORTED_LANGUAGES:
            continue

        # calculate final confidence as the product of detection confidence and language confidence
        detection_confidence *= lang_confidence

        if angle == 0:
            # give a bit more weight to unrotated image
            detection_confidence *= 1.1

        if detection_confidence > best_confidence:
            best_confidence = detection_confidence
            best_rotation = rotated
            best_text = text
            best_lang_confidence = lang_confidence
            # sufficient confidence to stop
            if best_confidence > 95:
                break

    return best_rotation, best_text, lang, best_lang_confidence


async def preprocess_ocr(image_path):
    # handle paths with non-ascii characters
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    gray = grayscale(image)
    blurred = blur(gray)
    closed = morpho(blurred)
    rotated, tesseract_text, tesseract_lang, tesseract_prob = await find_best_rotation(closed)
    return rotated, tesseract_text, tesseract_lang, tesseract_prob
