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
    'x-rar-compressed': 'rar',
    'x-7z-compressed': '7z',
    'x-tar': 'tar',
    'x-gzip': 'gz',
    'x-bzip2': 'bz2',
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
}

# create a magic object
mime = magic.Magic(mime=True)


# define a function to get the file format
def get_file_format(content_type, file_path):
    # try to use magic when tika fails
    if content_type == "unknown":
        content_type = mime.from_file(file_path)
        if not content_type or content_type == "":
            return "unknown"

    if '/' in content_type:
        content_type = content_type.split('/')[1].split(';')[0].lower()
    else:
        return content_type

    file_format = mime_mappings.get(content_type, "unknown")
    return file_format
