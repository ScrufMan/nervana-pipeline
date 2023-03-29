class FoundEntity:
    def __init__(self, filename, context, dataset, file_path, file_id):
        self.filename = filename
        self.context = context
        self.dataset = dataset
        self.file_path = file_path,
        self.file_id = file_id


def tag_term_in_context(context, search_term):
    return context.replace(search_term, f'<span class="text-danger font-weight-bold">{search_term}</span>')


def entities_from_hits(entity_hits, file_hits):
    entities = []

    files = []
    for file_hit in file_hits:
        files.append((file_hit.meta.id, file_hit.filename, file_hit.path))

    for entity_hit in entity_hits:
        for file_id, filename, file_path in files:
            if entity_hit.file_id == file_id:
                break
        else:
            filename = "Soubor nenalezen v Elasticsearch"
            file_path = ""

        context = tag_term_in_context(entity_hit.context, entity_hit.value)

        entity = FoundEntity(filename, context, entity_hit.meta.index, file_path, entity_hit.file_id)
        entities.append(entity)

    return entities
