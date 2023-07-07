import math

import cv2
import numpy as np
from pytesseract import pytesseract
from deskew import determine_skew
from .metadata import get_text_languages
from lingua import Language
from .common import blocking_to_async

LINGUA_TO_TESSERACT = {
    Language.CZECH: "ces",
    Language.ENGLISH: "eng",
    Language.FRENCH: "fra",
    Language.GERMAN: "deu",
    Language.ITALIAN: "ita",
    Language.POLISH: "pol",
    Language.SPANISH: "spa",
    Language.SLOVAK: "slk",
    Language.SLOVENE: "slv",
    Language.RUSSIAN: "rus",
    Language.UKRAINIAN: "ukr",
    Language.BULGARIAN: "bul",
    Language.DANISH: "dan",
    Language.DUTCH: "nld",
    Language.ESTONIAN: "est",
    Language.FINNISH: "fin",
    Language.GREEK: "ell",
    Language.HUNGARIAN: "hun",
    Language.LATVIAN: "lav",
    Language.LITHUANIAN: "lit",
    Language.PORTUGUESE: "por",
    Language.ROMANIAN: "ron",
    Language.SWEDISH: "swe",
    Language.TURKISH: "tur",
    Language.VIETNAMESE: "vie",
    Language.CHINESE: "chi_sim",
    Language.JAPANESE: "jpn",
    Language.KOREAN: "kor",
}


# gray-scaling
def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 15)
    return image


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# Rotate the image around its center
def rotate(
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


# skew correction
def deskew(image):
    angle = determine_skew(image)
    if angle:
        image = rotate(image, angle, (0, 0, 0))
    return image


def remove_borders(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_sorted = sorted(contours, key=lambda x: cv2.contourArea(x))
    cnt = cnts_sorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y + h, x:x + w]
    return crop


def preprocess(image_path):
    # to handle path with non-ascii characters
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8),
                         cv2.IMREAD_UNCHANGED)

    image = deskew(image)
    image = remove_noise(image)
    image = grayscale(image)
    image = thresholding(image)
    image = remove_borders(image)
    return image


async def extract_using_ocr(image_path):
    image = preprocess(image_path)
    text = await blocking_to_async(pytesseract.image_to_string, image, lang='ces+eng')

    langs = get_text_languages(text)
    if langs[0] == "unknown":
        return None

    langs = list(map(lambda x: LINGUA_TO_TESSERACT[x], filter(lambda x: x in LINGUA_TO_TESSERACT, langs)))
    lang_str = "+".join(langs)
    text = await blocking_to_async(pytesseract.image_to_string, image, lang=lang_str)
    return text, langs[0]
