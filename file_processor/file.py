import pathlib
import magic

from tika import parser
from .filters import *

from lingua import LanguageDetectorBuilder


class File:
    lang_detetctor = LanguageDetectorBuilder.from_all_languages().build()
    plaintext: str

    def __init__(self, path):
        self.path_obj = pathlib.PurePath(path)
        self.path = self.path_obj.__str__()
        self.filename = self.path_obj.stem
        self.extension = self.path_obj.suffix[1:]
        self.filetype = magic.from_file(path)
        self.processed = False
        self.plaintext = ""
        self.lang = None

    def process_file(self, do_filter=True):
        try:

            data = parser.from_file(self.path)
            raw = data["content"]

            if do_filter:
                raw = generic_filter(raw)

            self.plaintext = raw
            self.lang = self.lang_detetctor.detect_language_of(raw)
            self.processed = True


        except Exception as e:
            print(f"problem extracting text from file {self.path}:", e)
