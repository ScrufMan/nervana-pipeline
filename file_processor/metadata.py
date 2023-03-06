import magic


def get_file_format(path):
    raw_format = magic.from_file(path)

    if "PDF" in raw_format:
        file_format = "pdf"
    elif "Word" in raw_format:
        file_format = "doc"
    elif "PowerPoint" in raw_format:
        file_format = "pptx"
    elif "Rich Text" in raw_format:
        file_format = "rtf"
    elif "Unicode text" in raw_format or "ASCII text" in raw_format:
        file_format = "txt"
    else:
        file_format = "unknown"

    return file_format

