from .generic import generic_filter
from .pdf import filter_pdf
from .doc import filter_doc
from .pptx import filter_pptx

from typing import TYPE_CHECKING


def filter_plaintext(file):
    filtered_text = generic_filter(file.plaintext)

    match file.type:
        case "PDF":
            filtered_text = filter_pdf(filtered_text)
        case "DOC":
            filtered_text = filter_doc(filtered_text)
        case "PPTX":
            filtered_text = filter_pptx(filtered_text)

    file.plaintext = filtered_text
