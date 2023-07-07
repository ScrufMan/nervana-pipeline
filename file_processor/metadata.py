import sys

import magic
from lingua import LanguageDetectorBuilder, ConfidenceValue
from typing import Optional

mime_mappings = {
    'pdf': 'pdf',
    'msword': 'doc',
    'vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'vnd.ms-excel': 'xls',
    'vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'vnd.ms-powerpoint': 'ppt',
    'vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'xhtml+xml': 'html',
    'html': 'html',
    'plain': 'txt',
    'csv': 'csv',
    'rtf': 'rtf',
    'jpeg': 'jpeg',
    'jpg': 'jpg',
    'png': 'png',
    'gif': 'gif',
    'bmp': 'bmp',
    'tiff': 'tiff',
    'vnd.adobe.photoshop': 'psd',
    'svg+xml': 'svg',
    'vnd.ms-outlook': 'msg',
    'message/rfc822': 'eml',
    'calendar': 'ics',
    'vnd.oasis.opendocument.text': 'odt',
    'vnd.oasis.opendocument.spreadsheet': 'ods',
    'vnd.oasis.opendocument.presentation': 'odp',
    'zip': 'zip',
    'x-rar-compressed': 'zip',
    'x-7z-compressed': 'zip',
    'x-tar': 'zip',
    'x-gzip': 'zip',
    'x-bzip2': 'zip',
    'x-xz': 'xz',
    'x-msdownload': 'exe',
    'x-shockwave-flash': 'swf',
    'xml': 'xml',
    'json': 'json',
    'octet-stream': 'bin',
    'x-msvideo': 'avi',
    'mp4': 'mp4',
    'mpeg': 'mpeg',
    'x-matroska': 'mkv',
    'x-flv': 'flv',
    'webm': 'webm',
    'x-ms-wmv': 'wmv',
    'quicktime': 'mov',
    'x-ms-asf': 'asf',
    'mp3': 'mp3',
    'wav': 'wav',
    'ogg': 'ogg',
    'flac': 'flac',
    'x-realaudio': 'ra',
    'x-midi': 'mid',
    'x-aiff': 'aif',
    'x-mpegurl': 'm3u',
    'vnd.ms-spreadsheetml': 'xls',
}

# magic object
pymagic = magic.Magic(mime=True)
# language detector
lang_detector = LanguageDetectorBuilder.from_all_languages().build()


def parse_mime_type(mime_type) -> str:
    if isinstance(mime_type, list) and len(mime_type) > 0:
        mime_type = mime_type[0]
    if '/' in mime_type:
        mime_type = mime_type.split('/')[1]
    if ';' in mime_type:
        mime_type = mime_type.split(';')[0]

    mime_type = mime_type.lower()

    if mime_type in mime_mappings.values():
        return mime_type
    elif mime_type in mime_mappings.keys():
        return mime_mappings[mime_type]
    else:
        print(f"Unknown mime type: {mime_type}", file=sys.stderr)
        return ""


def get_file_format_magic(file_path):
    magic_mime = pymagic.from_file(file_path)
    return magic_mime


def get_text_languages(text) -> list[ConfidenceValue]:
    languages = lang_detector.compute_language_confidence_values(text)
    if not languages or languages[0].value < 0.5:
        # no reliable language detection
        return []

    # select only languages with a confidence > 0.3
    # since first language must have a confidence > 0.5 and other must have at least 0.3
    # this will always return at most two languages
    languages = map(lambda x: x, filter(lambda x: x.value > 0.3, languages))
    return list(languages)
