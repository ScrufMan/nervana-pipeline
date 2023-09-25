import os

from elasticsearch import AsyncElasticsearch, Elasticsearch


def get_async_elastic_client() -> AsyncElasticsearch:
    user = os.environ.get("ELASTIC_USER", None)
    password = os.environ.get("ELASTIC_PASSWORD", None)

    if user is None or password is None:
        raise EnvironmentError("ELASTIC_USER and ELASTIC_PASSWORD must be set in .env file")

    return AsyncElasticsearch(
        "https://localhost:9200",
        ca_certs="./http_ca.crt",
        basic_auth=(user, password),
        timeout=200
    )


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
