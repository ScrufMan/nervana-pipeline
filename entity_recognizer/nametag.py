from bs4 import BeautifulSoup
import requests
import re
from entity_recognizer.helper import get_context

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
    data = re.sub(r'\n', ' ', data)
    data = re.sub(r' {2,}', ' ', data)
    params = {'data': data}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']


def get_entities(tokenized_data, file_id):
    entities = []

    soup = BeautifulSoup(tokenized_data, "html.parser")

    tokenized_entities = soup.find_all("ne")

    for tokenized_entity in tokenized_entities:
        if tokenized_entity.parent not in soup.contents:  # means it's a part of container
            continue

        nametag_type = tokenized_entity.attrs["type"]

        universal_type = NAMETAG_TO_UNIVERSAL.get(nametag_type, "unknown")

        if universal_type == "unknown":
            continue

        entity_value = tokenized_entity.text

        context = get_context(entity_value, tokenized_entity.parent.text)

        entity = Entity(universal_type, entity_value, context, file_id)
        entities.append(entity)

    return entities


def run_nametag(data, file_id):
    tokenized = tokenize_data(data)
    found_entities = get_entities(tokenized, file_id)

    return found_entities
