import pathlib

from lingua import LanguageDetectorBuilder
from tika import parser

from .filters import filter_plaintext
from .filetype import get_filetype

FILTER = True

class File:
    lang_detetctor = LanguageDetectorBuilder.from_all_languages().build()

    def __init__(self, path):
        self.path_obj = pathlib.PurePath(path)
        self.path = self.path_obj.__str__()
        self.filename = self.path_obj.name
        self.type = get_filetype(path)
        self.plaintext = ""
        self.lang = None
        self.processed = False

    def process_file(self):
        try:

            data = parser.from_file(self.path)

            if data["status"] != 200:
                print(f"Error extracting plaintext from file {self.filename}")
                return

            self.plaintext = data["content"]

            if FILTER:
                filter_plaintext(self)

            self.lang = self.lang_detetctor.detect_language_of(self.plaintext)
            self.processed = True


        except Exception as e:
            print(f"problem extracting text from file {self.path}:", e)
