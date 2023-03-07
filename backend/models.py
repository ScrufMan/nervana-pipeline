class FoundEntity:
    def __init__(self, filename, context, dataset, file_path):
        self.filename = filename
        self.context = context
        self.dataset = dataset
        self.file_path = file_path


def tag_term_in_context(context, search_term):
    return context.replace(search_term, f'<span class="danger">{search_term}</span>')

def entities_from_hits(entity_hits, file_hits, search_term):
    entities = []

    files = []
    for file_hit in file_hits:
        files.append((file_hit["_id"], file_hit["_source"]["filename"], file_hit["_source"]["path"]))

    for entity_hit in entity_hits:
        for file_id, filename, file_path in files:
            if entity_hit["_source"]["file_id"] == file_id:
                break
        else:
            filename = "Soubor nenalezen v Elasticsearch"
            file_path = ""

        # context = tag_term_in_context(entity_hit["_source"]["context"], search_term)
        context = entity_hit["_source"]["context"]

        entity = FoundEntity(filename, context, entity_hit["_index"], file_path)
        entities.append(entity)

    return entities
