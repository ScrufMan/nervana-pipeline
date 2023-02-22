from bs4 import BeautifulSoup
import requests

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
    "A": "adress",
    "ah": "adress",
    "az": "adress",
    "gs": "adress",
    "gu": "city",
    "gc": "state",
    "at": "phone",
    "me": "email",
    "mi": "link",
    "if": "company",
    "io": "government"
}


def tokenize_data(data):
    url = f"{BASE_URL}/recognize"
    params = {'data': data}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']


def get_entities(tokenized_data):
    entities = []

    soup = BeautifulSoup(tokenized_data, "html.parser")

    tokenized_entities = soup.find_all("ne")

    for tokenized_entity in tokenized_entities:
        if tokenized_entity.parent not in soup.contents:  # means it's a part of container
            continue

        nametag_type = tokenized_entity.attrs["type"]

        universal_type = NAMETAG_TO_UNIVERSAL.get(nametag_type, "unknown")

        entity_tokens = tokenized_entity.find_all("token")
        entity_parts = list(map(lambda tag: tag.text, entity_tokens))
        entity_value = " ".join(entity_parts)

        entity = Entity(universal_type, entity_value, " ", 25)
        entities.append(entity)

    return entities

def run_nametag(data):
    tokenized = tokenize_data(data)
    entities = get_entities(tokenized)

    return entities

if __name__ == '__main__':
    sentence = "Václav Havel byl první prezident České republiky. A Milan Rastislav Štefánik generál armády. mail je " \
               "example@example.cz a + 420 944 168 220 z mesta 98401 Lučenec Slovensko, ulica Partizánska 7 a včera hrala. " \
               "O 19:00 tam bude i Vojtech tu je jeho mail vojtech@seznam.cz cislo je 0944168220 aj Peter Novák. Býva na ulici Partizánska 8, 98401 Lučenec. " \
               "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5"

    tokenized_sentences = tokenize_data(sentence)
    get_entities(tokenized_sentences)
