import json
import os

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk


async def assert_index_exists(es: AsyncElasticsearch, index_name: str):
    if await es.indices.exists(index=index_name):
        return

    wd_abs = os.getcwd()
    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        index_settings = json.load(config_file)["index"]

    await es.indices.create(index=index_name, body=index_settings)


# TODO: add file class as type
async def index_file(es: AsyncElasticsearch, dataset: str, file):
    file_document = file.make_document()
    res = await es.index(index=dataset, document=file_document)
    file_id = res['_id']

    actions = [
        {
            "_index": dataset,
            "_source": entity.make_document(file_id=file_id),
            "routing": file_id  # entity is child of file therefore it needs to be routed to the same shard
        }
        for entity in file.entities
    ]

    await async_bulk(es, actions)
