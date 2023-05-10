import os

from elasticsearch import AsyncElasticsearch, Elasticsearch
import json


def get_elastic_client() -> Elasticsearch:
    # absolute path of current working directory
    wd_abs = os.getcwd()
    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        config = json.load(config_file)
    return Elasticsearch([config], timeout=60)


def get_async_elastic_client() -> AsyncElasticsearch:
    # absolute path of current working directory
    wd_abs = os.getcwd()

    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        config = json.load(config_file)
    return AsyncElasticsearch([config], timeout=60)


async def test_connection(es: AsyncElasticsearch):
    # Check if connection can be established
    can_connect = await es.ping()
    if not can_connect:
        raise ConnectionError()
