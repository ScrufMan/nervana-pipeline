from lingua import Language

# -- General --

NUM_WORKERS = 4  # Number of worker coroutines
BATCH_WORKERS = 2  # Number of worker coroutines for batch NER processing
GPU = True  # Use GPU for available tasks

# -- Language detection --

SUPPORTED_LANGUAGES = [Language.CZECH, Language.SLOVAK, Language.ENGLISH, Language.DUTCH,
                       Language.GERMAN, Language.SPANISH, Language.UKRAINIAN]

# -- Entity recognition --

LANGUGAGE_TO_NAMETAG_MODEL = {
    Language.ENGLISH: "english-conll-200831",
    Language.CZECH: "czech-cnec2.0-200831",
    Language.SLOVAK: "czech-cnec2.0-200831",
    Language.DUTCH: "dutch-conll-200831",
    Language.GERMAN: "german-conll-200831",
    Language.SPANISH: "spanish-conll-200831",
    Language.UKRAINIAN: "ukrainian-languk-230306",
}  # mapping from language to nametag model

NAMETAG_TO_NERVANA = {
    "P": "person",
    "pc": "person",
    "pf": "person",
    "pp": "person",
    "p_": "person",
    "pm": "person",
    "ps": "person",
    "T": "datetime",
    "A": "location",
    "ah": "location",
    "az": "location",
    "gs": "location",
    "gu": "location",
    "gq": "location",
    "gc": "location",
    "g_": "location",
    "at": "phone",
    "me": "email",
    "mi": "link",
    "if": "organization",
    "io": "organization",
    "or": "document",
    "op": "product",
    "o_": "artifact",
}  # mapping from nametag entity types to NERvana types

MORPHODITA_TAGGER_PATH = "./czech.tagger"  # path to morphodita tagger

# -- OCR --

OCR_SUFFIXES = (".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp")  # files that can be processed by OCR
TESSERACT_LANG_STRING = "eng+ces+slk+pol+deu"
TESSERACT_CONFIG = r"--oem 3 --psm 6"
EASYOCR_LANGS = ["en", "cs", "sk", "pl", "de"]

# -- File processing --

TABULAR_FORMATS = [".csv", ".xls", ".xlsx"]  # formats that are considered tabular and duplicates should be removed
SUPPORTED_FORMATS = [
    '.pdf',
    '.doc',
    '.docx',
    '.xls',
    '.xlsx',
    '.ppt',
    '.pptx',
    '.html',
    '.html',
    '.txt',
    '.csv',
    '.rtf',
    '.jpeg',
    '.anb',
    '.jpg',
    '.png',
    '.gif',
    '.bmp',
    '.tiff',
    '.psd',
    '.svg',
    '.msg',
    '.eml',
    '.ics',
    '.odt',
    '.ods',
    '.odp',
    '.xz',
    '.exe',
    '.swf',
    '.xml',
    '.json',
    '.bin',
    '.avi',
    '.mp4',
    '.mpeg',
    '.mkv',
    '.flv',
    '.webm',
    '.wmv',
    '.mov',
    '.asf',
    '.mp3',
    '.wav',
    '.ogg',
    '.flac',
    '.ra',
    '.mid',
    '.aif',
    '.m3u',
    '.xls',
]
