import re


def generic_filter(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r'\n{3,}', '\n\n', raw)  # limit to at most 2 consecutive newlines
    raw = re.sub(r'\r', '', raw)  # remove carriage returns
    raw = re.sub(r' {2,}', ' ', raw)  # replace multiple spaces with a single space
    raw = re.sub(r'\t+', ' ', raw)  # replace multiple tabs with a single tab
    raw = re.sub(r'"', '', raw)  # remove double quotes
    raw = re.sub(r"'", '', raw)  # remove single quotes
    raw = re.sub(r'`', '', raw)  # remove backticks
    # filter to only printable characters
    raw = "".join([char for char in raw if char.isprintable()])
    return raw
