import spacy

from utils.text import get_context
from .entity import Entity

SPACY_TO_UNIVERSAL = {
    "PERSON": "person",
    "GPE": "location",
    "LOC": "location",
    "ORG": "organization",
    "PRODUCT": "product",
    "MONEY": "product",
    "WORK_OF_ART": "product",
    "EVENT": "product",
    "LAW": "document",
    "DATE": "datetime",
    "TIME": "datetime",
    "FAC": "location",
    "NORP": "organization",
}


def get_entities(data):
    entities = []
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(data)
    for ent in doc.ents:
        value = ent.text
        universal_type = SPACY_TO_UNIVERSAL.get(ent.label_, "unknown")
        if universal_type == "unknown":
            continue
        context = get_context(value, data)
        entity = Entity(universal_type, value, ent.lemma_, context)
        entities.append(entity)

    return entities
