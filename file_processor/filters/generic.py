import re


def generic_filter(raw:str) -> str:
    # Replace multiple consequent newlines with one
    raw = re.sub(r'\n{3,}', '\n', raw).strip()

    return raw