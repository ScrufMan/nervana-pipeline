import os

from elasticsearch import AsyncElasticsearch, Elasticsearch
import json


def get_elastic_client() -> Elasticsearch:
    # absolute path of current working directory
    wd_abs = os.getcwd()
    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        config = json.load(config_file)
    return Elasticsearch([config["host"], config["port"]], timeout=60)


def get_async_elastic_client() -> AsyncElasticsearch:
    # absolute path of current working directory
    wd_abs = os.getcwd()

    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        config = json.load(config_file)
    url = f"http://{config['host']}:{config['port']}"

    return AsyncElasticsearch(url, timeout=60)


async def test_connection(es: AsyncElasticsearch):
    # Check if connection can be established
    can_connect = await es.ping()
    if not can_connect:
        raise ConnectionError()
