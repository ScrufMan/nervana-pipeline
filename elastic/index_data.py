import asyncio
import json
import os
from typing import List

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk as bulk

from entity_recognizer import Entity
from file_processor import File


async def assert_index_exists(es: AsyncElasticsearch, index_name: str, config_path: str):
    if await es.indices.exists(index=index_name):
        return

    with open(config_path) as config_file:
        config = json.load(config_file)
    await es.indices.create(index=index_name, body=config)


async def assert_indices_exist(es: AsyncElasticsearch, dataset: str):
    wd_abs = os.getcwd()
    tasks = [
        assert_index_exists(es, f"{dataset}-files", os.path.join(wd_abs, "config/filesIndex.json")),
        assert_index_exists(es, f"{dataset}-entities", os.path.join(wd_abs, "config/entitiesIndex.json"))
    ]
    await asyncio.gather(*tasks)


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
