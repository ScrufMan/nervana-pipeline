from bs4 import BeautifulSoup
import requests

BASE_URL = "https://lindat.mff.cuni.cz/services/nametag/api"


def find_entity(soup, entity):
    entities = []

    tokenized_entities = soup.find_all("ne", {'type': entity})

    for entity in tokenized_entities:
        entity_tokens = entity.find_all("token")
        entity_parts = list(map(lambda tag: tag.text, entity_tokens))
        full_entity = " ".join(entity_parts)
        entities.append(full_entity)

    return entities


def find_uncontainerized_names(soup):
    names = []

    tokenized_entities = soup.find_all("ne", {'type': ["pf", "ps", "pm"]})

    for entity in tokenized_entities:
        if entity.parent in soup.contents:
            entity_tokens = entity.find_all("token")
            entity_parts = list(map(lambda tag: tag.text, entity_tokens))
            full_entity = " ".join(entity_parts)
            names.append(full_entity)

    return names


def recognize_data(data):
    url = f"{BASE_URL}/recognize"
    params = {'data': data}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']


def parse_data(data):
    soup = BeautifulSoup(data, "html.parser")

    names = find_entity(soup, "P")
    names.extend(find_uncontainerized_names(soup))
    emails = find_entity(soup, "me")
    phones = find_entity(soup, "at")

    output = f"""
    names: {names}
    emails: {emails}
    phones: {phones}
    """

    print(output)


sentence = "Václav Havel byl první prezident České republiky. A Milan Rastislav Štefánik generál armády. mail je " \
           "example@example.cz a +420944168220 z mesta 98401 Lučenec Slovensko, ulica Partizánska 7 a včera hrala. " \
           "O 19:00 tam bude i Vojtech tu je jeho mail vojtech@seznam.cz cislo je 0944168220 aj Peter Novák. Býva na ulici Partizánska 8, 98401 Lučenec."

tokenized_data = recognize_data(sentence)
parse_data(tokenized_data)
