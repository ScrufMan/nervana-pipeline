import spacy

SPACY_TO_UNIVERSAL = {
    "PERSON": "person",
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


def get_entities(data):
    nlp = spacy.load("en_core_web_sm")
    tokens = nlp(data)

    for token in tokens.ents:
        print(token)
