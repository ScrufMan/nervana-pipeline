import re


def generic_filter(raw: str, oneline) -> str:
    raw.strip()
    # Replace multiple consequent newlines with one
    raw = re.sub(r'\n{2,}', '\n', raw)
    raw = re.sub('\r', '', raw)
    raw = re.sub(r' {2,}', ' ', raw)
    raw = re.sub(r'"', '', raw)
    raw = re.sub(r"'", '', raw)
    if oneline:
        raw = re.sub(r'\n', '. ', raw)
    return raw
