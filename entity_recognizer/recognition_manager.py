from file_processor import File
from .nametag import run_nametag
from .spacy import get_entities
from lingua.language import Language

def find_entities_in_file(file: File):
    data = file.plaintext

    match file.lang:
        case Language.CZECH | Language.SLOVAK:
            return run_nametag(data)
        case _:
            return get_entities(data)
