from datetime import datetime
from pathlib import PurePath
from typing import Optional

from httpx import AsyncClient
from lingua import Language, IsoCode639_1
from neo4j import AsyncDriver

from config import config
from entity_recognizer import Entity
from entity_recognizer.recognition_manager import find_entities_in_file
from utils import setup_logger, filter_for_lang_detection, run_sync_fn_async_cpu, generic_filter
from .emails import process_email
from .metadata import extension_from_mime, determine_text_language
from .ocr import run_ocr
from .tika_client import call_tika_async

logger = setup_logger(__name__)


class File:
    def __init__(self, path: str, file_format: Optional[str] = None):
        self.path_obj = PurePath(path)
        self.format = file_format
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

    async def process(self, client: AsyncClient, neo4j_driver: AsyncDriver):
        tika_response = await call_tika_async(self.path, "meta")
        metadata = tika_response["metadata"]
        if not metadata:
            logger.error(f"{self}: cannot extract metadata using tika")
            return

        # use tika mime even if detected before by magic
        # use magic as fallback if available
        tika_mime = metadata.get("Content-Type")
        tika_extension = extension_from_mime(tika_mime)
        if tika_extension in config.SUPPORTED_FORMATS:
            self.format = tika_extension
        elif self.format is None:
            logger.error(f"{self}: cannot determine file format")
            return

        # handle emails
        if self.format in config.EMAIL_FORMATS:
            await process_email(neo4j_driver, self.path, metadata)

        if self.format in config.OCR_FROMATS:
            # language is detected by OCR because it's used for model selection
            plaintext, language = await run_sync_fn_async_cpu(run_ocr, self.path)
        else:
            tika_response = await call_tika_async(self.path, "text")
            plaintext = tika_response["content"] or ""
            plaintext = generic_filter(plaintext)
            filtered_text = filter_for_lang_detection(plaintext)
            language, _ = determine_text_language(filtered_text)

        if not plaintext:
            logger.error(f"{self}: cannot extract plaintext")
            return

        if not language or language not in config.SUPPORTED_LANGUAGES:
            # try to use language from tika
            tika_lang = metadata.get("language")
            if not tika_lang:
                logger.error(f"{self}: cannot determine language")
                return
            iso_code = IsoCode639_1[tika_lang.upper()]
            parsed_lang = Language.from_iso_code_639_1(iso_code)
            if parsed_lang in config.SUPPORTED_LANGUAGES:
                language = parsed_lang
            else:
                logger.error(f"{self}: unsupported language {language}")
                return

        self.plaintext = plaintext
        self.language = language
        self.timestamp = metadata.get("dcterms:created")
        self.author = metadata.get("dc:creator", "unknown")

        # file is marked as valid because if something goes wrong during entity recognition
        # at least the metadata and plaintext will be saved
        self.valid = True

        try:
            self.entities = await find_entities_in_file(client, self)
        except Exception as e:
            logger.error(f"{self}: Error while recognizing entities {e}")
            return

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
