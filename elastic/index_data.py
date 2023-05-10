import asyncio
import json
import os
from typing import List

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk as bulk

from entity_recognizer import Entity
from file_processor import File


async def assert_index_exists(es: AsyncElasticsearch, index_name: str):
    if await es.indices.exists(index=index_name):
        return

    wd_abs = os.getcwd()
    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        index_settings = json.load(config_file)["index"]

    await es.indices.create(index=index_name, body=index_settings)


async def index_file(es: AsyncElasticsearch, dataset: str, file: File) -> str:
    index_name = f"{dataset}-files"
    document = file.make_document()
    response = await es.index(index=index_name, document=document)
    return response["_id"]


async def index_entities(es: AsyncElasticsearch, dataset, entities: List[Entity]):
    index_name = f"{dataset}-entities"

    entities = map(lambda ent: ent.make_document(), entities)
    entities_actions = map(lambda ent: {"_index": index_name, "_source": ent}, entities)

    await bulk(es, entities_actions)
