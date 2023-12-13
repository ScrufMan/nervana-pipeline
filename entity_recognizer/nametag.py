import json

from bs4 import BeautifulSoup
from httpx import AsyncClient
from lingua.language import Language
from ufal.morphodita import *

from config import config
from utils.text import get_context
from .entity import Entity
from .post_processor import Lemmatizer, is_eligible_value

tagger = Tagger.load(config.MORPHODITA_TAGGER_PATH)


async def tokenize_data(client: AsyncClient, data: str, language: Language):
    # get base url from config
    # TODO: move to config.py
    with open("./config/nametag.json", "r") as config_file:
        base_url = json.load(config_file)["URL"]
    url = f"{base_url}/recognize"
    model = config.LANGUGAGE_TO_NAMETAG_MODEL[language]
    payload = {'data': data}
    response = await client.post(url, data=payload, params={"model": model})
    response.raise_for_status()
    return response.json()['result']


def get_entities(tokenized, is_tabular: bool) -> list[Entity]:
    entities = []
    entities_set = set()

    soup = BeautifulSoup(tokenized, "html.parser")

    tokenized_entities = soup.find_all("ne")

    for tokenized_entity in tokenized_entities:
        if tokenized_entity.parent not in soup.contents:  # means it's a part of a container and will be processed later
            continue

        entity_value = tokenized_entity.text

        if not is_eligible_value(entity_value):
            continue

        # skip duplicates if we're processing tabular data
        if is_tabular:
            if entity_value.lower() in entities_set:
                continue
            entities_set.add(entity_value.lower())

        nametag_type = tokenized_entity.attrs["type"]
        nervana_type = config.NAMETAG_TO_NERVANA.get(nametag_type)

        if not nervana_type:
            continue

        try:
            lemmatized_value = Lemmatizer.lemmatize_text(entity_value, tagger)
        except Exception as e:
            print(f"Failed to lemmatize {entity_value}, error: {e}")
            lemmatized_value = entity_value

        context = get_context(entity_value, tokenized_entity.parent.text)

        entity = Entity(nervana_type, entity_value, lemmatized_value, context)
        entities.append(entity)

    return entities


async def run_nametag(client: AsyncClient, plaintext: str, language: Language, is_tabular: bool) -> list[Entity]:
    tokenized = await tokenize_data(client, plaintext, language)
    found_entities = get_entities(tokenized, is_tabular)

    return found_entities
