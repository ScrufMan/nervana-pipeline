import sys

import magic

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

# create a magic object
mime = magic.Magic(mime=True)


def get_file_format(metadata, file_path):
    # tika
    content_type = metadata.get("Content-Type", "unknown")
    # try to use magic when tika fails
    if content_type == "unknown":
        content_type = mime.from_file(file_path)
        if not content_type:
            return "unknown"

    if isinstance(content_type, list):
        content_type = content_type[0]
    if '/' in content_type:
        content_type = content_type.split('/')[1].split(';')[0].lower()

    if content_type in mime_mappings.values():
        return content_type
    elif content_type in mime_mappings.keys():
        return mime_mappings[content_type]

    print(f"Unknown file format: {content_type}", file=sys.stderr)
    return "unknown"

