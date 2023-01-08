import re


def filter_pdf(raw: str):
    # Remove duplicate '\n'
    raw = re.sub(r'\n{3,}', '\n', raw).strip()

    return raw
