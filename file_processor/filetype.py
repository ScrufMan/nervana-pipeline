from enum import Enum

import magic

class FileType(Enum):
    UNKNOWN = 1
    PDF = 2
    DOC = 3
    PPTX = 4
    TXT = 5


def get_filetype(path):
    raw_type = magic.from_file(path)

    if "PDF" in raw_type:
        filetype = FileType.PDF
    elif "Word" in raw_type:
        filetype = FileType.DOC
    elif "PowerPoint" in raw_type:
        filetype = FileType.PPTX
    elif "Unicode text" in raw_type or "ASCII text" in raw_type:
        filetype = FileType.TXT
    else:
        filetype = FileType.UNKNOWN

    return filetype
