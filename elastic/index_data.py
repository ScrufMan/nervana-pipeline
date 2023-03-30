from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from entity_recognizer import Entity
from file_processor import File


def create_index_if_not_exists(es: Elasticsearch, index_name):
    # Check if index exists
    try:
        es.indices.get(index=index_name)
        return
    except NotFoundError:
        # If index does not exist, create it
        mapping = {
            "mappings": {
                "properties": {
                    "type": {"type": "keyword"},
                    "filename": {"type": "text"},
                    "format": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "path": {"type": "text"},
                    "timestamp": {"type": "date"},
                    "context": {"type": "text"},
                    "entity_type": {"type": "keyword"},
                    "file_id": {"type": "keyword"},
                    "value": {"type": "text"},
                    "lematized": {"type": "text"}
                }
            }
        }

        es.indices.create(index=index_name, body=mapping)


def index_file(es: Elasticsearch, index_name, file: File):
    document = file.make_document()
    response = es.index(index=index_name, document=document)
    return response["_id"]


def index_entities(es: Elasticsearch, index_name, entities: List[Entity]):
    for entity in entities:
        document = entity.make_document()
        es.index(index=index_name, document=document)
