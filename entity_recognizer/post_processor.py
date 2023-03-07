import re
from entity_recognizer.entity import Entity
from entity_recognizer.helper import get_context


def find_phone_numbers(data, phones):
    matches = re.findall("\\+?[0-9]{8,14}|\+ *[0-9]{3} *[0-9]{3} *[0-9]{3} *[0-9]{3}", data)

    for match in matches:
        if match not in phones:
            # model has detected phone number without prefix
            if match[1:].strip() in phones:
                phones.remove(match[1:].strip())

            phones.append(match)


def find_btc_adresses(plaintext, file_id):
    btc_adresses = []
    matches = re.findall(r"([13]|bc1)[A-HJ-NP-Za-km-z1-9]{27,34}", plaintext)
    for match in matches:
        context = get_context(match, plaintext)
        entity = Entity("btc_adress", match, context, file_id)
        btc_adresses.append(entity)
    return btc_adresses


def find_ibans(plaintext, file_id):
    ibans = []
    matches = re.findall(
        r'[a-zA-Z]{2}[0-9]{2}\s?[a-zA-Z0-9]{4}\s?[0-9]{4}\s?[0-9]{3}([a-zA-Z0-9]\s?[a-zA-Z0-9]{0,4}\s?[a-zA-Z0-9]{0,4}\s?[a-zA-Z0-9]{0,4}\s?[a-zA-Z0-9]{0,3})?',
        plaintext)
    for match in matches:
        context = get_context(match, plaintext)
        entity = Entity("bank_account", match, context, file_id)
        ibans.append(entity)
    return ibans
