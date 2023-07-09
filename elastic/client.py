import json
import os

from elasticsearch import AsyncElasticsearch, Elasticsearch


def get_sync_elastic_client() -> Elasticsearch:
    # absolute path of current working directory
    wd_abs = os.getcwd()

    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        config = json.load(config_file)
    url = f"http://{config['host']}:{config['port']}"
    return Elasticsearch(url, timeout=200)


def get_async_elastic_client() -> AsyncElasticsearch:
    # absolute path of current working directory
    wd_abs = os.getcwd()

    with open(os.path.join(wd_abs, "config/elastic.json")) as config_file:
        config = json.load(config_file)
    url = f"http://{config['host']}:{config['port']}"

    return AsyncElasticsearch(url, timeout=200)


async def test_connection_async(es: AsyncElasticsearch):
    # Check if connection can be established
    can_connect = await es.ping()
    if not can_connect:
        raise ConnectionError()


def test_connection_sync(es: Elasticsearch):
    # Check if connection can be established
    can_connect = es.ping()
    if not can_connect:
        raise ConnectionError()
