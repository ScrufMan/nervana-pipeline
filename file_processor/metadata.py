import mimetypes

import magic
from lingua import LanguageDetectorBuilder, Language

# magic object
pymagic = magic.Magic(mime=True)

# language detector
lang_detector = LanguageDetectorBuilder.from_all_spoken_languages().build()


def extension_from_mime(mime_type: str | None) -> str | None:
    if not mime_type:
        return None
    # remove additional information
    mime_type = mime_type.split(";")[0]
    if mime_type == "application/x-anb":
        return ".anb"
    return mimetypes.guess_extension(mime_type)


def get_file_format_magic(file_path) -> str:
    mime = pymagic.from_file(file_path)
    if mime == "text/rtf":
        mime = "application/rtf"
    if mime == "application/vnd.ms-office" and file_path.endswith(".anb"):
        mime = "application/x-anb"
    return mime


def determine_text_language(text: str) -> tuple[Language | None, float]:
    languages = lang_detector.compute_language_confidence_values(text)
    if not languages or languages[0].value < 0.6:
        # no reliable language detection
        return None, 0

    # return the most probable language
    return languages[0].language, languages[0].value
