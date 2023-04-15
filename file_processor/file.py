import pathlib
from datetime import datetime

from lingua import LanguageDetectorBuilder
from tika import parser

from .filters import filter_plaintext
from .metadata import get_file_format

FILTER = True
lang_detetctor = LanguageDetectorBuilder.from_all_languages().build()


class File:
    def __init__(self, path):
        self.path_obj = pathlib.PurePath(path)
        self.path = self.path_obj.__str__()
        self.filename = self.path_obj.name
        self.format = get_file_format(path)
        self.original_plaintext = ""
        self.plaintext = ""
        self.lang = None
        self.author = None
        self.timestamp = None

    def process_file(self):
        try:
            tika_response = parser.from_file(self.path)

            if tika_response["status"] != 200:
                print(f"Error extracting plaintext from file {self.filename}")
                return False

            self.plaintext = tika_response["content"]
            self.original_plaintext = tika_response["content"]
            self.timestamp = tika_response["metadata"].get("Creation-Date", datetime.now())
            self.author = tika_response["metadata"].get("Author", None)
            self.lang = lang_detetctor.detect_language_of(self.plaintext).iso_code_639_1.name.lower()

            if FILTER:
                filter_plaintext(self)

            return True

        except Exception as e:
            print(f"problem extracting text from file {self.path}:", e)
            return False

    def make_document(self):
        document = {
            "filename": self.filename,
            "path": self.path,
            "format": self.format,
            "plaintext": self.original_plaintext,
            "language": self.lang.name.lower(),
            "author": self.author,
            "timestamp": self.timestamp
        }

        return document
