import json

from bs4 import BeautifulSoup
import requests
import re
from entity_recognizer.helper import get_context
from entity_recognizer.post_processor import lemmatize_text

from .entity import Entity

BASE_URL = "https://lindat.mff.cuni.cz/services/nametag/api"

NAMETAG_TO_UNIVERSAL = {
    "P": "person",
    "pc": "person",
    "pf": "person",
    "pp": "person",
    "p_": "person",
    "pm": "person",
    "ps": "person",
    "T": "datetime",
    "A": "location",
    "ah": "location",
    "az": "location",
    "gs": "location",
    "gu": "location",
    "gq": "location",
    "gc": "location",
    "at": "phone",
    "me": "email",
    "mi": "link",
    "if": "organization",
    "io": "organization",
    "or": "document",
    "op": "product"
}


def tokenize_data(data):
    url = f"{BASE_URL}/recognize"
    payload = {'data': data}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()['result']
    else:
        raise Exception(f"Nametag failed with status code {response.status_code}, message: {response.text}")


def get_entities(tokenized):
    entities = []

    soup = BeautifulSoup(tokenized, "html.parser")

    tokenized_entities = soup.find_all("ne")

    for tokenized_entity in tokenized_entities:
        if tokenized_entity.parent not in soup.contents:  # means it's a part of container
            continue

        nametag_type = tokenized_entity.attrs["type"]
        universal_type = NAMETAG_TO_UNIVERSAL.get(nametag_type, "unknown")

        if universal_type == "unknown":
            continue

        entity_value = tokenized_entity.text

        try:
            lemmatized_value = lemmatize_text(entity_value)
        except Exception as e:
            print(f"Failed to lemmatize {entity_value}, error: {e}")
            lemmatized_value = entity_value

        context = get_context(entity_value, tokenized_entity.parent.text)

        entity = Entity(universal_type, entity_value, lemmatized_value, context)
        entities.append(entity)

    return entities


def run_nametag(plaintext: str):
    tokenized = tokenize_data(plaintext)
    found_entities = get_entities(tokenized)

    return found_entities
