import spacy
from lingua import Language

from config import config
from entity_recognizer import Entity
from entity_recognizer.post_processor import is_eligible_value
from utils import get_context


def run_spacy(plaintext: str, language: Language, is_tabular: bool) -> list[Entity]:
    entities = []
    entities_set = set()
    model = config.LANGUAGE_TO_SPACY_MODEL[language]

    nlp = spacy.load(model)
    doc = nlp(plaintext)

    for ent in doc.ents:
        entity_value = ent.text
        nervana_type = config.SPACY_TO_NERVANA.get(ent.label_)

        if not is_eligible_value(entity_value, nervana_type):
            continue
        # skip duplicates if we're processing tabular data
        if is_tabular:
            if entity_value.lower() in entities_set:
                continue
            entities_set.add(entity_value.lower())

        context = get_context(entity_value, plaintext)
        entity = Entity(nervana_type, entity_value, ent.lemma_, context)
        entities.append(entity)

    return entities
