class Entity:
    def __init__(self, entity_type, value, lemmatized, context, file_id):
        self.entity_type = entity_type
        self.value = value
        self.lemmatized = lemmatized
        self.context = context
        self.file_id = file_id

    def make_document(self):
        document = {
            "entity_type": self.entity_type,
            "value": self.value,
            "lemmatized": self.lemmatized,
            "context": self.context,
            "file_id": self.file_id
        }

        return document
