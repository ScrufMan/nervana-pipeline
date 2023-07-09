from .generic import generic_filter
from .pdf import filter_pdf
from .doc import filter_doc
from .pptx import filter_pptx


def filter_plaintext(file_format, plaintext, from_ocr=False):
    filtered_text = generic_filter(plaintext, from_ocr)

    match file_format:
        case "pdf":
            filtered_text = filter_pdf(filtered_text)
        case "doc":
            filtered_text = filter_doc(filtered_text)
        case "pptx":
            filtered_text = filter_pptx(filtered_text)

    return filtered_text
