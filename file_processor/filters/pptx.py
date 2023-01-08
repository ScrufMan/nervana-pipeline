import re


def filter_pptx(raw: str):
    # remove metadata
    raw = re.sub(r'[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]\nAnnual Review\n‹#›', '\n', raw)

    # Remove duplicate '\n'
    raw = re.sub(r'\n{3,}', '\n', raw).strip()

    return raw
