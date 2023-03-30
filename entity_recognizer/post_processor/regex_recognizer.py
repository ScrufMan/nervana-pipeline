import re
from entity_recognizer.entity import Entity
from entity_recognizer.helper import get_context
from . import lemmatize_text


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
    matches = re.findall(r"[13][a-km-zA-HJ-NP-Z1-9]{25,34}", plaintext)
    for match in matches:
        context = get_context(match, plaintext)
        entity = Entity("btc_adress", match, lemmatize_text(match), context, file_id)
        btc_adresses.append(entity)
    return btc_adresses


def find_bank_accounts(plaintext, file_id):
    ibans = []
    matches = re.findall(
        r'\b[A-Z]{2}\s*\d{2}\s*(?:\d\s*){4,20}\b',
        plaintext)
    for match in matches:
        context = get_context(match, plaintext)
        entity = Entity("bank_account", match, lemmatize_text(match), context, file_id)
        ibans.append(entity)
    return ibans