from bs4 import BeautifulSoup
import requests

from .post_processor import find_phone_numbers, find_bitcoin_adresses

BASE_URL = "https://lindat.mff.cuni.cz/services/nametag/api"


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


def find_entities_by_type(soup, entity_type):
    entities = []

    tokenized_entities = soup.find_all("ne", {'type': entity_type})

    for tokenized_entity in tokenized_entities:
        entity_tokens = tokenized_entity.find_all("token")
        entity_parts = list(map(lambda tag: tag.text, entity_tokens))
        entity = " ".join(entity_parts)
        entities.append(entity)

    if entity_type == "P":
        entities.extend(find_uncontainerized_names(soup))

    return entities


def recognize_data(data):
    url = f"{BASE_URL}/recognize"
    params = {'data': data}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']


def parse_data(data, plaintext):
    soup = BeautifulSoup(data, "html.parser")

    names = find_entities_by_type(soup, "P")
    emails = find_entities_by_type(soup, "me")
    phones = find_entities_by_type(soup, "at")
    companies = find_entities_by_type(soup, "if")
    links = find_entities_by_type(soup, "mi")
    countries = find_entities_by_type(soup, "gc")

    find_phone_numbers(plaintext, phones)

    btc_adresses = find_bitcoin_adresses(plaintext)

    output = f"""
    names: {names}
    emails: {emails}
    phones: {phones}
    companies: {companies}
    links: {links}
    countries: {countries}
    btc_adresses: {btc_adresses}
    """

    print(output)

    result = {
        "names": names,
        "emails": emails,
        "phones": phones,
        "companies": companies,
        "links": links,
        "countries": countries,
        "btc_adresses": btc_adresses
    }

    return result


if __name__ == '__main__':
    sentence = "Václav Havel byl první prezident České republiky. A Milan Rastislav Štefánik generál armády. mail je " \
               "example@example.cz a + 420 944 168 220 z mesta 98401 Lučenec Slovensko, ulica Partizánska 7 a včera hrala. " \
               "O 19:00 tam bude i Vojtech tu je jeho mail vojtech@seznam.cz cislo je 0944168220 aj Peter Novák. Býva na ulici Partizánska 8, 98401 Lučenec. " \
               "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5"

    tokenized_data = recognize_data(sentence)
    parse_data(tokenized_data)
