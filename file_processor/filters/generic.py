import re


def generic_filter(raw: str) -> str:
    raw.strip()
    # Replace multiple consequent newlines with one
    raw = re.sub(r'\n{2,}', '\n', raw)
    raw = re.sub('\r', '', raw)
    raw = re.sub(r' {2,}', ' ', raw)
    raw = re.sub(r'"', '', raw)
    raw = re.sub(r"'", '', raw)
    return raw
