import asyncio
import sys
from pathlib import PurePath
from datetime import datetime
from typing import Optional

from httpx import AsyncClient

from entity_recognizer import Entity
from entity_recognizer.recognition_manager import find_entities_in_file
from lingua import Language

from .ocr import run_ocr
from .tika import get_tika_metadata, get_tika_content

from .filters import filter_plaintext
from .metadata import get_file_format_magic, parse_mime_type, get_text_languages
import keras_ocr


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
        metadata = await get_tika_metadata(self.path)

        mime_format = metadata.get("Content-Type", "")
        if mime_format == "":
            # try to get file format from magic
            mime_format = get_file_format_magic(self.path)

        file_format = parse_mime_type(mime_format)
        if not file_format or file_format in ["zip"]:
            return

        # file is handled by ocr
        ocr_type = file_format in ["png", "jpg", "jpeg", "tiff"]
        if ocr_type:
            plaintext, language = await run_ocr(self.path)
        else:
            plaintext = await get_tika_content(self.path)
            langs = get_text_languages(plaintext)
            language = langs[0].language if langs else None

        if not plaintext:
            print(f"File {self.path} has no content", file=sys.stderr)
            return

        if not language:
            print(f"File {self.path} couldn't determine language", file=sys.stderr)
            return

        plaintext = filter_plaintext(file_format, plaintext, ocr_type)

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
