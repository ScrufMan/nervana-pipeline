import os
import pathlib
import tika

from tika import parser
from .filters import *

from lingua import Language, LanguageDetectorBuilder

LANGUAGES = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.CZECH, Language.SLOVAK]


class File:
    plaintext: str

    def __init__(self, path):
        self.path = path
        self.path_obj = pathlib.PurePath(path)
        self.filename = self.path_obj.stem
        self.extension = self.path_obj.suffix[1:]
        self.processed = False
        self.plaintext = ""
        self.lang = None

    def extract_plaintext(self, do_filter=True):
        try:
            data = parser.from_file(self.path)
            raw = data["content"]

            if do_filter:
                match self.extension:
                    case "pdf":
                        raw = filter_pdf(raw)

                    case "doc" | "docx":
                        raw = filter_doc(raw)

                    case "pptx":
                        raw = filter_pptx(raw)

            self.plaintext = raw



        except Exception as e:
            print(f"problem extracting text from file {self.path}:", e)

    def detect_language(self):
        if self.plaintext is "":
            return

        detector = LanguageDetectorBuilder.from_languages(*LANGUAGES).build()
        self.lang = detector.detect_language_of(self.plaintext)
