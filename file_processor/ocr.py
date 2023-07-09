import sys
from typing import Optional

import easyocr
from lingua import Language, ConfidenceValue
from pytesseract import pytesseract

from .common import blocking_to_async
from .filters import generic_filter
from .image_preprocessor import preprocess
from .metadata import get_text_languages

# load this model into memory and keep it here, since czech is the most common language
czech_easyocr_reader = easyocr.Reader(["cs"], gpu=False)

available_tess_languages = pytesseract.get_languages()
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


async def run_tesseract(preprocessed_image, langs):
    lang_str = "+".join(langs) if langs else None
    text = await blocking_to_async(pytesseract.image_to_string, preprocessed_image, lang=lang_str)
    text = text.lower()
    return text


async def run_easyocr(preprocessed_image, langs):
    reader = czech_easyocr_reader if langs == ["cs"] else easyocr.Reader(langs, gpu=False)
    results = await blocking_to_async(reader.readtext, preprocessed_image, detail=0)
    text = " ".join([result for result in results])
    text = text.lower()
    return text


def get_most_probable_langs(langs_tess: list[ConfidenceValue], langs_easyocr: list[ConfidenceValue]) -> str:
    """
    Determine which model yields better language probability, therefor which model has better results
    :param langs_tess: list of languages with their probability from tesseract
    :param langs_easyocr: list of languages with their probability from easyocr
    :return: "tesseract" or "easyocr" depending on which model has better results
    """
    if not langs_tess and not langs_easyocr:
        return ""

    if not langs_tess:
        return "easyocr"

    if not langs_easyocr:
        return "tesseract"

    return "easyocr" if langs_easyocr[0].value > langs_tess[0].value else "tesseract"


async def run_ocr(image_path) -> tuple[Optional[str], Optional[Language]]:
    image, initial_text = await preprocess(image_path)

    initial_langs = get_text_languages(initial_text)
    if not initial_langs:
        # no meaningful text
        print(f"{image_path} OCR found no meaningful text", file=sys.stderr)
        return None, None

    langs = initial_langs

    # convert most probable languages to tesseract and easyocr language code
    tesseract_langs_code = [cv.language.iso_code_639_3.name.lower() for cv in langs if
                            cv.language.iso_code_639_3.name.lower() in available_tess_languages]
    easyocr_lang_codes = [cv.language.iso_code_639_1.name.lower() for cv in langs if
                          cv.language.iso_code_639_1.name.lower() in available_easyocr_languages]

    # run ocr again with the most probable languages
    tesseract_text = await run_tesseract(image, tesseract_langs_code)
    tesseract_langs = get_text_languages(tesseract_text)

    easyocr_text = await run_easyocr(image, easyocr_lang_codes)
    easyocr_langs = get_text_languages(easyocr_text)

    better_model = get_most_probable_langs(tesseract_langs, easyocr_langs)
    if not better_model:
        # all models failed to obtained meaningful text
        print(f"{image_path} OCR found no meaningful text", file=sys.stderr)
        return None, None

    text = easyocr_text if better_model == "easyocr" else tesseract_text
    langs = easyocr_langs if better_model == "easyocr" else tesseract_langs
    lang = langs[0].language

    return text, lang
