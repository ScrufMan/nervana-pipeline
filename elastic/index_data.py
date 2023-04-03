from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import bulk

from file_processor import File
from entity_recognizer import Entity


def create_files_index(es, dataset):
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


def create_entities_index(es, dataset):
    entity_index_name = f'{dataset}-entities'

    analysis = {
        "filter": {
            "asciifolding_custom": {
                "type": "asciifolding",
                "preserve_original": True
            },
            "czech_stop": {
                "type": "stop",
                "stopwords": "_czech_"
            },
            "czech_stemmer": {
                "type": "stemmer",
                "language": "czech"
            },
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            },
            "english_stemmer": {
                "type": "stemmer",
                "language": "english"
            }
        },
        "analyzer": {
            "czech_value": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["czech_stop", "lowercase", "czech_stemmer", "asciifolding_custom"]
            },
            "english_value": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["english_stop", "lowercase", "english_stemmer", "asciifolding_custom"]
            },
            "czech_lemmatized": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "asciifolding_custom"]
            },
            "english_lemmatized": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "asciifolding_custom"]
            }
        }
    }

    entity_mappings = {
        "properties": {
            "entity_type": {"type": "keyword"},
            "value": {
                "type": "text",
                "analyzer": "czech_value",
                "fields": {
                    "english": {
                        "type": "text",
                        "analyzer": "english_value"
                    }
                }
            },
            "lemmatized": {
                "type": "text",
                "analyzer": "czech_lemmatized",
                "fields": {
                    "english": {
                        "type": "text",
                        "analyzer": "english_lemmatized"
                    }
                }
            },
            "context": {"type": "text"},
            "file_id": {"type": "keyword"}
        }

    }
    settings = {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": analysis
    }

    es.indices.create(index=entity_index_name,
                      body={
                          "settings": settings,
                          "mappings": entity_mappings
                      })


def create_index_if_not_exists(es: Elasticsearch, dataset):
    # Check if index exists
    if not es.indices.exists(index=f"{dataset}-files"):
        create_files_index(es, dataset)
        create_entities_index(es, dataset)


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
