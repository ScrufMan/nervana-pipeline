from file_processor import File
from .nametag import run_nametag
from .spacy import get_entities
from lingua.language import Language

def find_entities_in_plaintext(plaintext, lang: Language, file_id):

    match lang:
        case Language.CZECH | Language.SLOVAK:
            return run_nametag(plaintext, file_id)
        case _:
            return get_entities(plaintext)
