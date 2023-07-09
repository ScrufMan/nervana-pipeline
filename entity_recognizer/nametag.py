import json

from bs4 import BeautifulSoup
from httpx import AsyncClient
from lingua.language import Language
from ufal.morphodita import *

from .entity import Entity
from .helpers import get_context
from .post_processor.lemmatizer import Lemmatizer

tagger = Tagger.load(r"C:\Users\bukaj\code\school\bakalarka\entity_recognizer\post_processor\czech.tagger")

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
    "g_": "location",
    "at": "phone",
    "me": "email",
    "mi": "link",
    "if": "organization",
    "io": "organization",
    "or": "document",
    "op": "product",
    "o_": "artifact",
}

LANGUGAGE_TO_MODEL = {
    Language.ENGLISH: "english-conll-200831",
    Language.CZECH: "czech-cnec2.0-200831",
    Language.SLOVAK: "czech-cnec2.0-200831",
    Language.DUTCH: "dutch-conll-200831",
    Language.GERMAN: "german-conll-200831",
    Language.SPANISH: "spanish-conll-200831",
    Language.UKRAINIAN: "ukrainian-languk-230306",
}


async def tokenize_data(client: AsyncClient, data: str, language: Language):
    # get base url from config
    with open("./config/nametag.json", "r") as config_file:
        base_url = json.load(config_file)["URL"]
    url = f"{base_url}/recognize"
    model = LANGUGAGE_TO_MODEL[language]
    payload = {'data': data}
    response = await client.post(url, data=payload, params={"model": model})
    response.raise_for_status()
    return response.json()['result']


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
            lemmatized_value = Lemmatizer.lemmatize_text(entity_value, tagger)
        except Exception as e:
            print(f"Failed to lemmatize {entity_value}, error: {e}")
            lemmatized_value = entity_value

        context = get_context(entity_value, tokenized_entity.parent.text)

        entity = Entity(universal_type, entity_value, lemmatized_value, context)
        entities.append(entity)

    return entities


async def run_nametag(client: AsyncClient, plaintext: str, language: Language):
    tokenized = await tokenize_data(client, plaintext, language)
    found_entities = get_entities(tokenized)

    return found_entities
