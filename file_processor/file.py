import asyncio
import sys
from pathlib import PurePath
from datetime import datetime
from typing import Optional

from httpx import AsyncClient

from entity_recognizer import Entity
from entity_recognizer.recognition_manager import find_entities_in_file
from exceptions import *
from functools import partial
from lingua import LanguageDetectorBuilder, Language
from tika import parser

from .filters import filter_plaintext
from .metadata import get_file_format

FILTER = True
lang_detector = LanguageDetectorBuilder.from_all_languages().build()


class File:
    def __init__(self, path: str):
        self.path_obj = PurePath(path)
        self.format = "unknown"
        self.plaintext = ""
        self.language: Optional[Language] = None
        self.author = "unknown"
        self.timestamp: Optional[datetime] = None
        self.entities: list[Entity] = []
        self.valid = False

    @property
    def path(self):
        return self.path_obj.__str__()

    @property
    def filename(self):
        return self.path_obj.name

    async def process(self, client: AsyncClient):
        try:
            loop = asyncio.get_event_loop()
            tika_parser = partial(parser.from_file, self.path)
            tika_response = await loop.run_in_executor(None, tika_parser)
        except Exception as e:
            raise TikaError(f"Error while parsing file {self.path}: {e}")

        if tika_response["status"] != 200:
            raise TikaError(f"{tika_response['status']}: {tika_response['statusMessage']}")

        metadata = tika_response["metadata"]
        file_format = get_file_format(metadata, self.path)

        if file_format in ["unknown", "zip"]:
            return

        content = tika_response["content"]
        if not content:
            print(f"File {self.path} has no content", file=sys.stderr)
            return
        if not isinstance(content, str):
            raise TikaError("Tika returned unknown content")

        plaintext: str = content
        if FILTER:
            plaintext = filter_plaintext(file_format, plaintext)

        language = lang_detector.detect_language_of(plaintext)
        if not language:
            print(f"File {self.path} unknown language", file=sys.stderr)
            return

        self.format = file_format
        self.plaintext = plaintext
        self.language = language
        self.timestamp = metadata.get("dcterms:created", datetime.now())
        self.author = metadata.get("dc:creator", "unknown")

        try:
            entities = await find_entities_in_file(client, self)
        except Exception as e:
            print(f"Error while recognizing entities in file {self.path}: {e}", file=sys.stderr)
            return

        if not entities:
            print(f"File {self.path} has no entities")
            return

        self.entities = entities
        self.valid = True

    def make_document(self):
        return {
            "filename": self.filename,
            "path": self.path,
            "format": self.format,
            "plaintext": self.plaintext,
            "language": self.language.iso_code_639_1.name.lower() if self.language else "unknown",
            "author": self.author,
            "timestamp": self.timestamp,
            "entities": [entity.make_document() for entity in self.entities]
        }

    def __str__(self):
        return f"File({self.filename})"

    def __repr__(self):
        return self.__str__()
