import os
import pathlib
import tika

from tika import parser


from lingua import Language, LanguageDetectorBuilder

LANGUAGES = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH, Language.CZECH, Language.SLOVAK]


class File:
    def __init__(self, path):
        tika.initVM()
        self.path = path
        self.path_obj = pathlib.PurePath(path)
        self.filename = self.path_obj.stem
        self.extension = self.path_obj.suffix
        self.processed = False
        self.plaintext = None
        self.lang = None

    def extract_plaintext(self):
        try:
            data = parser.from_file(self.path)
            self.plaintext = data["content"]

        except Exception as e:
            print(f"problem extracting text from file {self.path}:", e)

    def detect_language(self):
        if self.plaintext is None:
            return

        detector = LanguageDetectorBuilder.from_languages(*LANGUAGES).build()
        self.lang = detector.detect_language_of(self.plaintext)
