from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk

from file_processor import File
from entity_recognizer import Entity


def create_index_if_not_exists(es: Elasticsearch, dataset):
    # Check if index exists
    try:
        es.indices.get(index=f"{dataset}-files")
        return
    except NotFoundError:
        # If index does not exist, create it

        # create index for files
        file_index_name = f'{dataset}-files'
        file_mappings = {
            'mappings': {
                'properties': {
                    'filename': {'type': 'text'},
                    'path': {'type': 'text'},
                    'format': {'type': 'keyword'},
                    'plaintext': {'type': 'text'},
                    'language': {'type': 'keyword'},
                    'author': {'type': 'text'},
                    'timestamp': {'type': 'date'},
                }
            }
        }
        es.indices.create(index=file_index_name, body=file_mappings)

        # create index for entities
        entity_index_name = f'{dataset}-entities'
        entity_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "lemmatized_lowercase": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "asciifolding"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "entity_type": {"type": "text"},
                    "value": {"type": "text"},
                    "lemmatized": {
                        "type": "text",
                        "analyzer": "lemmatized_lowercase"
                    },
                    "context": {"type": "text"},
                    "file_id": {"type": "keyword"}
                }
            }
        }
        es.indices.create(index=entity_index_name, body=entity_settings)


def index_file(es: Elasticsearch, dataset, file: File):
    index_name = f"{dataset}-files"
    document = file.make_document()
    response = es.index(index=index_name, document=document)
    return response["_id"]


def index_entities(es: Elasticsearch, dataset, entities: List[Entity]):
    index_name = f"{dataset}-entities"

    entities = map(lambda ent: ent.make_document(), entities)
    entities_actions = map(lambda ent: {"_index": index_name, "_source": ent}, entities)

    bulk(es, entities_actions)
