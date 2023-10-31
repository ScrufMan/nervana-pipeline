import asyncio
from typing import Optional

import easyocr
from colorama import Fore, Style
from lingua import Language
from pytesseract import pytesseract

from config import config
from file_processor.filters import generic_filter
from file_processor.image_preprocessor import preprocess_ocr
from file_processor.metadata import determine_text_language
from utils import run_sync_fn_async, filter_for_lang_detection

# load this model into memory and keep it here, since czech is the most common language
easyocr_reader = easyocr.Reader(config.EASYOCR_LANGS, gpu=config.GPU)

available_easyocr_languages = ["abq",
                               "ady",
                               "af",
                               "ang",
                               "ar",
                               "as",
                               "ava",
                               "az",
                               "be",
                               "bg",
                               "bh",
                               "bho",
                               "bn",
                               "bs",
                               "ch_sim",
                               "ch_tra",
                               "che",
                               "cs",
                               "cy",
                               "da",
                               "dar",
                               "de",
                               "en",
                               "es",
                               "et",
                               "fa",
                               "fr",
                               "ga",
                               "gom",
                               "hi",
                               "hr",
                               "hu",
                               "id",
                               "inh",
                               "is",
                               "it",
                               "ja",
                               "kbd",
                               "kn",
                               "ko",
                               "ku",
                               "la",
                               "lez",
                               "lt",
                               "lv",
                               "mah",
                               "mai",
                               "mi",
                               "mn",
                               "mr",
                               "ms",
                               "mt",
                               "ne",
                               "new",
                               "nl",
                               "no",
                               "oc",
                               "pi",
                               "pl",
                               "pt",
                               "ro",
                               "ru",
                               "rs_cyrillic",
                               "rs_latin",
                               "sck",
                               "sk",
                               "sl",
                               "sq",
                               "sv",
                               "sw",
                               "ta",
                               "tab",
                               "te",
                               "th",
                               "tjk",
                               "tl",
                               "tr",
                               "ug",
                               "uk",
                               "ur",
                               "vi",
                               "uz"]


async def run_tesseract(preprocessed_image):
    text = await run_sync_fn_async(pytesseract.image_to_string, preprocessed_image, lang=config.TESSERACT_LANG_STRING)

    text = generic_filter(text)
    text = text.lower()
    filtered_text = filter_for_lang_detection(text)
    return text, filtered_text


async def run_easyocr(preprocessed_image):
    data = await run_sync_fn_async(easyocr_reader.readtext, preprocessed_image, detail=0)
    text = " ".join(data)
    text = generic_filter(text)
    text = text.lower()
    filtered_text = filter_for_lang_detection(text)

    return text, filtered_text


def determine_better_model(tess_prob: int | None, easyocr_prob: int | None) -> str:
    """
    Determine which model yields better language probability, therefor which model has better results
    :param langs_tess: list of languages with their probability from tesseract
    :param langs_easyocr: list of languages with their probability from easyocr
    :return: "tesseract" or "easyocr" depending on which model has better results
    """
    if not tess_prob and not easyocr_prob:
        return ""

    if tess_prob == 0:
        return "easyocr"

    if easyocr_prob == 0:
        return "tesseract"

    # easyocr usually has better results, so we give it a bit more weight
    easyocr_prob *= 1.1

    return "easyocr" if easyocr_prob > tess_prob else "tesseract"


async def run_ocr(image_path) -> tuple[Optional[str], Optional[Language]]:
    print(f"Preprocessing image {image_path}")
    image_preprocessed, tesseract_text, tesseract_lang, tesseract_prob = await preprocess_ocr(image_path)

    easyocr_text, easyocr_filtered = await run_easyocr(image_preprocessed)

    easyocr_lang, easyocr_prob = determine_text_language(easyocr_filtered, ocr=True)
    if not easyocr_lang or easyocr_lang not in config.SUPPORTED_LANGUAGES:
        easyocr_lang = None
        easyocr_prob = 0

    better_model = determine_better_model(tesseract_prob, easyocr_prob)
    if not better_model:
        # all models failed to obtained meaningful text
        print(f"{Fore.MAGENTA}{image_path}: OCR found no meaningful text{Style.RESET_ALL}")
        return None, None

    text = easyocr_text if better_model == "easyocr" else tesseract_text
    lang = easyocr_lang if better_model == "easyocr" else tesseract_lang

    return text, lang


asyncio.run(run_ocr(
    r"/Users/scrufman/code/school/bakalarka/nervana-pipeline/data/PPR-189_ČJ-2020-990340-FAU JI/101716 Tomášek Martin/ID.jpg"))
