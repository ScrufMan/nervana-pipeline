class Entity:
    def __init__(self, entity_type, value, lematized, context, file_id):
        self.entity_type = entity_type
        self.value = value
        self.lematized = lematized
        self.context = context
        self.file_id = file_id

    def make_document(self):
        document = {
            "type": "entity",
            "entity_type": self.entity_type,
            "value": self.value,
            "lematized ": self.lematized,
            "context": self.context,
            "file_id": self.file_id
        }

        return document
