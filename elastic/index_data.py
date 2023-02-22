from typing import List

from elasticsearch import Elasticsearch

from entity_recognizer import Entity

def index_data(entities: List[Entity], index, client: Elasticsearch):
    for entity in entities:
        document = entity.make_document()
        response = client.index(index=index, document=document)
