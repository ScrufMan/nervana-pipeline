import re
import textwrap

from config.config import CONTEXT_LENGTH


def generic_filter(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r'\n{3,}', '\n\n', raw)  # limit to at most 2 consecutive newlines
    raw = re.sub(r'\r', '', raw)  # remove carriage returns
    raw = re.sub(r' {2,}', ' ', raw)  # replace multiple spaces with a single space
    raw = re.sub(r'\t+', ' ', raw)  # replace tabs with a single space
    raw = re.sub(r'"', '', raw)  # remove double quotes
    raw = re.sub(r"'", '', raw)  # remove single quotes
    raw = re.sub(r'`', '', raw)  # remove backticks
    # filter to only printable characters
    raw = "".join([char for char in raw if char.isprintable() or char == '\n'])
    return raw


def filter_for_lang_detection(text: str):
    # filter text to only alphanumeric characters with space for better language detection
    filtered_text = ""
    for char in text:
        if char.isalnum() or char.isspace():
            filtered_text += char
    return filtered_text


def get_context(value, parent):
    start_idx = parent.find(value)
    end_idx = start_idx + len(value) - 1

    parent_end_idx = len(parent) - 1
    one_direction_len = (CONTEXT_LENGTH - len(value)) // 2

    if one_direction_len <= 0:
        return value

    start_idx -= one_direction_len
    end_idx += one_direction_len

    if start_idx < 0:
        end_idx += -start_idx
        start_idx = 0

    if end_idx > parent_end_idx:
        offset = end_idx - parent_end_idx
        start_idx = max(0, start_idx - offset)

    return parent[start_idx:end_idx + 1]


def split_string(s, length):
    return textwrap.wrap(s, length)
