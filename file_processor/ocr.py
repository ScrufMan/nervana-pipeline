import math
import sys

import cv2
import keras_ocr
import numpy as np
from deskew import determine_skew
from lingua import Language, ConfidenceValue
from pytesseract import pytesseract

from .common import blocking_to_async
from .filters import generic_filter
from .metadata import get_text_languages

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
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
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
    image = grayscale(image)
    # image = remove_noise(image)
    # image = thresholding(image)
    # image = remove_borders(image)
    return image


async def run_tesseract(preprocessed_image, langs):
    lang_str = "+".join(langs)
    text_raw = await blocking_to_async(pytesseract.image_to_string, preprocessed_image, lang=lang_str)
    text = generic_filter(text_raw, oneline=True)
    return text


async def run_keras(preprocessed_image):
    keras_pipeline = keras_ocr.pipeline.Pipeline()
    keras_img = keras_ocr.tools.read(preprocessed_image)
    prediction_groups = await blocking_to_async(keras_pipeline.recognize, [keras_img])
    detected_img = prediction_groups[0]
    raw_text = " ".join(map(lambda x: x[0], detected_img))
    text = generic_filter(raw_text, oneline=True)
    return text


def get_most_probable_langs(langs_tess: list[ConfidenceValue], langs_keras: list[ConfidenceValue]) -> str:
    if not langs_tess and not langs_keras:
        return ""

    if not langs_tess:
        return "keras"

    if not langs_keras:
        return "tesseract"

    return "keras" if langs_keras[0].value > langs_tess[0].value else "tesseract"


async def extract_using_ocr(image_path):
    image = preprocess(image_path)
    # assuming most of the text is in czech with some english
    tesseract_text = await run_tesseract(image, ["ces", "eng"])
    keras_text = await run_keras(image)

    langs_tess = get_text_languages(tesseract_text)
    langs_keras = get_text_languages(keras_text)

    better_model = get_most_probable_langs(langs_tess, langs_keras)
    if not better_model:
        # all models failed to obtained meaningful text
        print(f"{image_path} OCR found no useful text", file=sys.stderr)
        return None, None

    langs = langs_keras if better_model == "keras" else langs_tess

    # convert most probable language to tesseract language code
    tesseract_langs_code = list(
        map(lambda x: LINGUA_TO_TESSERACT[x.language], filter(lambda x: x.language in LINGUA_TO_TESSERACT, langs)))

    # run tesseract again with the most probable languages
    tesseract_text = await run_tesseract(image, tesseract_langs_code)
    langs_tess = get_text_languages(tesseract_text)

    better_model = get_most_probable_langs(langs_tess, langs_keras)
    if not better_model:
        # all models failed to obtained meaningful text
        print(f"{image_path} OCR found no useful text", file=sys.stderr)
        return None, None

    text = keras_text if better_model == "keras" else tesseract_text
    langs = langs_keras if better_model == "keras" else langs_tess

    return text, langs[0]
