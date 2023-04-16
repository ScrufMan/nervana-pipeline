from .nametag import run_nametag
from .spacy import get_entities
from lingua.language import Language
from entity_recognizer.post_processor import find_btc_adresses, find_bank_accounts

def find_entities_in_plaintext(plaintext, language: Language, file_id):

    match language:
        case Language.CZECH | Language.SLOVAK:
            entities_in_file = run_nametag(plaintext, file_id)
        case _:
            entities_in_file = get_entities(plaintext)

    entities_in_file.extend(find_btc_adresses(plaintext, file_id))
    entities_in_file.extend(find_bank_accounts(plaintext, file_id))

    return entities_in_file
