from datetime import datetime

from file_processor import File


class Entity:
    def __init__(self, category, value, context, language, filepath):
        self.category = category
        self.value = value
        self.context = context
        self.language = language
        self.filepath = filepath

    def make_document(self):
        document = {
            "category": self.category,
            "value": self.value,
            "context": self.context,
            "language": self.language.name,
            "filepath": self.filepath,
            "timestamp": datetime.now()
        }

        return document

def make_entities(data, file: File):
    all_entities = []
    for category, category_values in data.items():
        for value in category_values:
            entity = Entity(category, value, " ", file.lang, file.path)
            all_entities.append(entity)

    return all_entities

