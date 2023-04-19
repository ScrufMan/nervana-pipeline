import asyncio
from pathlib import PurePath
from datetime import datetime
from typing import Optional, List

from entity_recognizer import Entity
from .exceptions import *
from functools import partial
from lingua import LanguageDetectorBuilder, Language
from tika import parser

from .filters import filter_plaintext
from .metadata import get_file_format

FILTER = True
lang_detetctor = LanguageDetectorBuilder.from_all_languages().build()


class File:
    def __init__(self, path: str):
        self.path_obj: PurePath = PurePath(path)
        self.path: str = self.path_obj.__str__()
        self.filename: str = self.path_obj.name
        self.format: str = "unknown"
        self.plaintext: str = ""
        self.language: Optional[Language] = None
        self.author = "unknown"
        self.timestamp: datetime = datetime.now()
        self.entities: List[Entity] = []

    async def process(self):
        loop = asyncio.get_event_loop()
        tika_parser = partial(parser.from_file, self.path)
        tika_response = await loop.run_in_executor(None, tika_parser)

        if tika_response["status"] != 200:
            raise TikaError(f"{tika_response['status']}: {tika_response['statusMessage']}")

        content = tika_response["content"]
        if not content:
            raise NoFileContentError()

        if not isinstance(content, str):
            raise TikaError("Tika returned unknown content")

        plaintext: str = content.strip()
        self.plaintext = plaintext

        metadata = tika_response["metadata"]

        self.format = get_file_format(metadata.get("Content-Type", "unknown"), self.path)
        self.timestamp = metadata.get("Creation-Date", datetime.now())
        self.author = metadata.get("Author", "Unknown")
        self.language = lang_detetctor.detect_language_of(self.plaintext)

        if FILTER:
            filter_plaintext(self)

    def make_document(self):
        document = {
            "filename": self.filename,
            "path": self.path,
            "format": self.format,
            "plaintext": self.plaintext,
            "language": self.language.iso_code_639_1.name.lower() if self.language else "unknown",
            "author": self.author,
            "timestamp": self.timestamp
        }

        return document
