class FoundEntity:
    def __init__(self, filename, context, dataset, file_path, file_id):
        self.filename = filename
        self.context = context
        self.dataset = dataset
        self.file_path = file_path
        self.file_id = file_id


def tag_term_in_context(context, search_term):
    return context.replace(search_term, f'<span class="text-danger font-weight-bold">{search_term}</span>')


def entities_from_hits(entity_hits):
    entities = []

    for entity_hit in entity_hits:
        context = tag_term_in_context(entity_hit.context, entity_hit.value)
        dataset = entity_hit.meta.index

        filename = entity_hit.meta.inner_hits["file"].hits[0].filename
        file_path = entity_hit.meta.inner_hits["file"].hits[0].path
        file_id = entity_hit.entities.parent

        entity = FoundEntity(filename, context, dataset, file_path, file_id)
        entities.append(entity)

    return entities
