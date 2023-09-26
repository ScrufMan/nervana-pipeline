from datetime import datetime
from pathlib import PurePath
from typing import Optional

from colorama import Fore, Style
from httpx import AsyncClient
from lingua import Language, IsoCode639_1

from entity_recognizer import Entity
from entity_recognizer.recognition_manager import find_entities_in_file
from .filters import filter_plaintext
from .metadata import get_file_format_magic, parse_mime_type, determine_text_languages
from .tika import get_tika_data, get_tika_language

# TODO: move to config
supported_languages = [Language.CZECH, Language.SLOVAK, Language.ENGLISH, Language.DUTCH,
                       Language.GERMAN, Language.SPANISH, Language.UKRAINIAN]


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
        metadata, plaintext = await get_tika_data(self.path)

        mime_format = metadata.get("Content-Type")
        if not mime_format:
            # try to get file format from magic
            mime_format = get_file_format_magic(self.path)

        file_format = parse_mime_type(mime_format)
        if not file_format:
            print(f"{Fore.LIGHTMAGENTA_EX}{self}: unknown mime type: {mime_format}{Style.RESET_ALL}")
            return
        if file_format in ["zip"]:
            return

        if not plaintext:
            print(f"{Fore.LIGHTMAGENTA_EX}{self}: has no content{Style.RESET_ALL}")
            return

        language = determine_text_languages(plaintext)

        if not language or language not in supported_languages:
            # try to use language from tika
            tika_lang = await get_tika_language(self.path)
            iso_code = IsoCode639_1[tika_lang.upper()]
            parsed_lang = Language.from_iso_code_639_1(iso_code)
            if parsed_lang in supported_languages:
                language = parsed_lang
            else:
                print(f"{Fore.LIGHTMAGENTA_EX}{self}: unsupported language {language}{Style.RESET_ALL}")
                return

        plaintext = filter_plaintext(file_format, plaintext)

        self.format = file_format
        self.plaintext = plaintext
        self.language = language
        self.timestamp = metadata.get("dcterms:created", datetime.now())
        self.author = metadata.get("dc:creator", "unknown")

        # file is marked as valid because if something goes wrong during entity recognition
        # at least the metadata and plaintext will be saved
        self.valid = True

        try:
            entities = await find_entities_in_file(client, self)
        except Exception as e:
            print(f"{Fore.RED}{self}: Error while recognizing entities {e}{Style.RESET_ALL}")
            return

        self.entities = entities

    def make_document(self):
        return {
            "filename": self.filename,
            "path": self.path,
            "format": self.format,
            "plaintext": self.plaintext,
            "language": self.language.iso_code_639_1.name.lower(),
            "author": self.author,
            "timestamp": self.timestamp,
            "entities": {
                "name": "file",
            }
        }

    def __str__(self):
        return f"File({self.path})"

    def __repr__(self):
        return self.__str__()
