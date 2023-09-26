import re


def generic_filter(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r'\n{2,}', '\n', raw)
    raw = re.sub('\r', '', raw)
    raw = re.sub(r' {2,}', ' ', raw)
    raw = re.sub(r'\t{2,}', '\t', raw)
    raw = re.sub(r'\t', ' ', raw)
    raw = re.sub(r'"', '', raw)
    raw = re.sub(r"'", '', raw)
    return raw
