import pathlib
from datetime import datetime

from .exceptions import *

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
        self.format = None
        self.original_plaintext = ""
        self.plaintext = ""
        self.lang = None
        self.author = None
        self.timestamp = None

    def process_file(self):
        tika_response = parser.from_file(self.path)
        if tika_response["status"] != 200:
            raise TikaError(f"{tika_response['status']}: {tika_response['statusMessage']}")

        plaintext = tika_response["content"]
        if not plaintext:
            raise NoFileContentError()

        self.plaintext = plaintext
        self.original_plaintext = plaintext

        metadata = tika_response["metadata"]

        self.format = get_file_format(metadata.get("Content-Type", "unknown"), self.path)
        self.timestamp = metadata.get("Creation-Date", datetime.now())
        self.author = metadata.get("Author", "Unknown")
        self.lang = lang_detetctor.detect_language_of(self.plaintext)

        if FILTER:
            filter_plaintext(self)

    def make_document(self):
        document = {
            "filename": self.filename,
            "path": self.path,
            "format": self.format,
            "plaintext": self.original_plaintext,
            "language": self.lang.iso_code_639_1.name.lower(),
            "author": self.author,
            "timestamp": self.timestamp
        }

        return document
